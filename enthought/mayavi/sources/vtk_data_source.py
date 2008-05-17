"""This source manages a VTK dataset given to it.  When this source is
pickled or persisted, it saves the data given to it in the form of a
gzipped string.
"""
# Author: Prabhu Ramachandran <prabhu_r@users.sf.net>
# Copyright (c) 2005-2006, Enthought, Inc.
# License: BSD Style.

# Enthought library imports.
from enthought.traits.api import Instance, List, Str, Bool, Int
from enthought.traits.ui.api import View, Group, Item
from enthought.persistence.state_pickler \
     import gzip_string, gunzip_string, set_state
from enthought.tvtk.api import tvtk
from enthought.tvtk import messenger

# Local imports.
from enthought.mayavi.core.source import Source
from enthought.mayavi.core.common import handle_children_state
from enthought.mayavi.core.traits import DEnum
from vtk_xml_file_reader import get_all_attributes


######################################################################
# `VTKDataSource` class
######################################################################
class VTKDataSource(Source):

    """This source manages a VTK dataset given to it.  When this
    source is pickled or persisted, it saves the data given to it in
    the form of a gzipped string.

    Note that if the VTK dataset has changed internally and you need
    to notify the mayavi pipeline to flush the data just call the
    `modified` method of the VTK dataset and the mayavi pipeline will
    update automatically.
    """

    # The version of this class.  Used for persistence.
    __version__ = 0

    # The VTK dataset to manage.
    data = Instance(tvtk.DataSet, allow_none=False)
    
    ########################################
    # Dynamic traits: These traits are dynamic and are updated on the
    # _update_data method.

    # The active point scalar name.
    point_scalars_name = DEnum(values_name='_point_scalars_list',
                               desc='scalar point data attribute to use')
    # The active point vector name.
    point_vectors_name = DEnum(values_name='_point_vectors_list',
                               desc='vectors point data attribute to use')
    # The active point tensor name.
    point_tensors_name = DEnum(values_name='_point_tensors_list',
                               desc='tensor point data attribute to use')

    # The active cell scalar name.
    cell_scalars_name = DEnum(values_name='_cell_scalars_list',
                               desc='scalar cell data attribute to use')
    # The active cell vector name.
    cell_vectors_name = DEnum(values_name='_cell_vectors_list',
                               desc='vectors cell data attribute to use')
    # The active cell tensor name.
    cell_tensors_name = DEnum(values_name='_cell_tensors_list',
                               desc='tensor cell data attribute to use')

    ########################################
    # Our view.

    view = View(Group(Item(name='point_scalars_name'),
                      Item(name='point_vectors_name'),
                      Item(name='point_tensors_name'),
                      Item(name='cell_scalars_name'),
                      Item(name='cell_vectors_name'),
                      Item(name='cell_tensors_name'),
                      Item(name='data'),
                      ))

    ########################################
    # Private traits.

    # These private traits store the list of available data
    # attributes.  The non-private traits use these lists internally.
    _point_scalars_list = List(Str)
    _point_vectors_list = List(Str)
    _point_tensors_list = List(Str)
    _cell_scalars_list = List(Str)
    _cell_vectors_list = List(Str)
    _cell_tensors_list = List(Str)
    
    # This filter allows us to change the attributes of the data
    # object and will ensure that the pipeline is properly taken care
    # of.  Directly setting the array in the VTK object will not do
    # this.
    _assign_attribute = Instance(tvtk.AssignAttribute, args=(),
                                 allow_none=False)

    # Toggles if this is the first time this object has been used.
    _first = Bool(True)

    # The ID of the observer for the data.
    _observer_id = Int(-1)
    
    ######################################################################
    # `object` interface
    ######################################################################
    def __get_pure_state__(self):
        d = super(VTKDataSource, self).__get_pure_state__()
        for name in ('_assign_attribute', '_first', '_observer'):
            d.pop(name, None)
        for name in ('point_scalars', 'point_vectors',
                     'point_tensors', 'cell_scalars',
                     'cell_vectors', 'cell_tensors'):
            d.pop('_' + name + '_list', None)
            d.pop('_' + name + '_name', None)
        data = self.data
        if data is not None:
            w = tvtk.DataSetWriter(write_to_output_string=1)
            warn = w.global_warning_display
            w.set_input(data)
            w.global_warning_display = 0
            w.update()
            w.global_warning_display = warn
            z = gzip_string(w.output_string)
            d['data'] = z
        return d

    def __set_pure_state__(self, state):
        z = state.data
        if z is not None:
            d = gunzip_string(z)
            r = tvtk.DataSetReader(read_from_input_string=1,
                                   input_string=d)
            r.update()
            self.data = r.output
        # Now set the remaining state without touching the children.
        set_state(self, state, ignore=['children', 'data'])
        # Setup the children.
        handle_children_state(self.children, state.children)
        # Setup the children's state.
        set_state(self, state, first=['children'], ignore=['*'])

    ######################################################################
    # `Base` interface
    ######################################################################
    def start(self):
        """This is invoked when this object is added to the mayavi
        pipeline.
        """
        # Do nothing if we are already running.
        if self.running:
            return

        # Update the data just in case.
        self._update_data()

        # Call the parent method to do its thing.  This will typically
        # start all our children.
        super(VTKDataSource, self).start()

    def update(self):
        """Invoke this to flush data changes downstream.  This is
        typically used when you change the data object and want the
        mayavi pipeline to refresh.
        """        
        # This tells the VTK pipeline that the data has changed.  This
        # will fire the data_changed event automatically.
        self.data.modified()

    ######################################################################
    # Non-public interface
    ######################################################################
    def _data_changed(self, old, new):
        aa = self._assign_attribute
        aa.input = new
        self._update_data()
        self.outputs = [aa.output]
        self.data_changed = True

        # Add an observer to the VTK dataset after removing the one
        # for the old dataset.  We use the messenger to avoid an
        # uncollectable reference cycle.  See the
        # enthought.tvtk.messenger module documentation for details.
        if old is not None:
            old.remove_observer(self._observer_id)
        self._observer_id = new.add_observer('ModifiedEvent',
                                             messenger.send)
        new_vtk = tvtk.to_vtk(new)
        messenger.connect(new_vtk, 'ModifiedEvent',
                          self._fire_data_changed)
        
        # Change our name so that our label on the tree is updated.
        self.name = self._get_name()

    def _fire_data_changed(self, *args):
        """Simply fire the `data_changed` event."""
        self.data_changed = True
    
    def _set_data_name(self, data_type, attr_type, value):
        if value is None:
            return

        dataset = self.data
        if len(value) == 0:
            # If the value is empty then we deactivate that attribute.
            d = getattr(dataset, attr_type + '_data')
            method = getattr(d, 'set_active_%s'%data_type)
            method(None)
            self.data_changed = True
            return

        aa = self._assign_attribute
        data = None
        if attr_type == 'point':
            data = dataset.point_data
        elif attr_type == 'cell':
            data = dataset.cell_data
        method = getattr(data, 'set_active_%s'%data_type)
        method(value)
        aa.assign(value, data_type.upper(), attr_type.upper() +'_DATA')
        aa.update()
        # Fire an event, so the changes propagate.
        self.data_changed = True

    def _point_scalars_name_changed(self, value):
        self._set_data_name('scalars', 'point', value)

    def _point_vectors_name_changed(self, value):
        self._set_data_name('vectors', 'point', value)

    def _point_tensors_name_changed(self, value):
        self._set_data_name('tensors', 'point', value)

    def _cell_scalars_name_changed(self, value):
        self._set_data_name('scalars', 'cell', value)

    def _cell_vectors_name_changed(self, value):
        self._set_data_name('vectors', 'cell', value)

    def _cell_tensors_name_changed(self, value):
        self._set_data_name('tensors', 'cell', value)
    
    def _update_data(self):
        if self.data is None:
            return
        pnt_attr, cell_attr = get_all_attributes(self.data)
        
        def _setup_data_traits(obj, attributes, d_type):
            """Given the object, the dict of the attributes from the
            `get_all_attributes` function and the data type
            (point/cell) data this will setup the object and the data.
            """
            attrs = ['scalars', 'vectors', 'tensors']
            aa = obj._assign_attribute
            data = getattr(obj.data, '%s_data'%d_type)
            for attr in attrs:
                values = attributes[attr]
                values.append('')
                setattr(obj, '_%s_%s_list'%(d_type, attr), values)
                if len(values) > 1:
                    default = getattr(obj, '%s_%s_name'%(d_type, attr))
                    if obj._first and len(default) == 0:
                        default = values[0]
                    getattr(data, 'set_active_%s'%attr)(default)
                    aa.assign(default, attr.upper(),
                              d_type.upper() +'_DATA')
                    aa.update()
                    kw = {'%s_%s_name'%(d_type, attr): default,
                          'trait_change_notify': False}
                    obj.set(**kw)

        _setup_data_traits(self, pnt_attr, 'point')
        _setup_data_traits(self, cell_attr, 'cell')
        if self._first:
            self._first = False
        # Propagate the data changed event.
        self.data_changed = True
        
    def _get_name(self):
        """ Gets the name to display on the tree.
        """
        ret = "VTK Data (uninitialized)"
        if self.data is not None:
            typ = self.data.__class__.__name__
            ret = "VTK Data (%s)"%typ
        if '[Hidden]' in self.name:
            ret += ' [Hidden]'
        return ret
