# Automatically generated code: EDIT AT YOUR OWN RISK
from traits import api as traits
from traitsui import api as traitsui

from tvtk import vtk_module as vtk
from tvtk import tvtk_base
from tvtk.tvtk_base_handler import TVTKBaseHandler
from tvtk import messenger
from tvtk.tvtk_base import deref_vtk
from tvtk import array_handler
from tvtk.array_handler import deref_array
from tvtk.tvtk_classes.tvtk_helper import wrap_vtk

from tvtk.tvtk_classes.xml_writer import XMLWriter


class XMLDataSetWriter(XMLWriter):
    """
    XMLDataSetWriter - Write any type of VTK XML file.
    
    Superclass: XMLWriter
    
    XMLDataSetWriter is a wrapper around the VTK XML file format
    writers.  Given an input DataSet, the correct writer is
    automatically selected based on the type of input.
    
    See Also:
    
    XMLImageDataWriter XMLStructuredGridWriter
    XMLRectilinearGridWriter XMLPolyDataWriter
    XMLUnstructuredGridWriter
    
    """
    def __init__(self, obj=None, update=True, **traits):
        tvtk_base.TVTKBase.__init__(self, vtk.vtkXMLDataSetWriter, obj, update, **traits)
    
    def _get_input(self):
        try:
            return wrap_vtk(self._vtk_obj.GetInput(0))
        except TypeError:
            return wrap_vtk(self._vtk_obj.GetInput())
    def _set_input(self, obj):
        old_val = self._get_input()
        self._wrap_call(self._vtk_obj.SetInput, deref_vtk(obj))
        self.trait_property_changed('input', old_val, obj)
    input = traits.Property(_get_input, _set_input,
                            help="The first input of this object, i.e. the result of `get_input(0)`.")
    
    def get_input(self):
        """
        V.get_input() -> DataSet
        C++: DataSet *GetInput()
        Get/Set the writer's input.
        """
        ret = wrap_vtk(self._vtk_obj.GetInput())
        return ret
        

    def set_input(self, *args):
        """
        V.set_input(DataObject)
        C++: void SetInput(DataObject *)
        V.set_input(int, DataObject)
        C++: void SetInput(int, DataObject *)
        Set/Get an input of this algorithm. You should not override these
        methods because they are not the only way to connect a pipeline
        """
        my_args = [deref_vtk(x) for x in args]
        ret = self._wrap_call(self._vtk_obj.SetInput, *my_args)
        return ret

    _updateable_traits_ = \
    (('byte_order', 'GetByteOrder'), ('global_warning_display',
    'GetGlobalWarningDisplay'), ('file_name', 'GetFileName'),
    ('progress_text', 'GetProgressText'), ('debug', 'GetDebug'),
    ('data_mode', 'GetDataMode'), ('time_step_range', 'GetTimeStepRange'),
    ('number_of_time_steps', 'GetNumberOfTimeSteps'),
    ('encode_appended_data', 'GetEncodeAppendedData'),
    ('release_data_flag', 'GetReleaseDataFlag'), ('progress',
    'GetProgress'), ('reference_count', 'GetReferenceCount'),
    ('time_step', 'GetTimeStep'), ('block_size', 'GetBlockSize'),
    ('abort_execute', 'GetAbortExecute'), ('id_type', 'GetIdType'))
    
    _full_traitnames_list_ = \
    (['abort_execute', 'debug', 'encode_appended_data',
    'global_warning_display', 'release_data_flag', 'byte_order',
    'data_mode', 'id_type', 'block_size', 'file_name',
    'number_of_time_steps', 'progress_text', 'time_step',
    'time_step_range'])
    
    def trait_view(self, name=None, view_element=None):
        if view_element is not None or name not in (None, '', 'traits_view', 'full_traits_view', 'view'):
            return super(XMLDataSetWriter, self).trait_view(name, view_element)
        if name == 'full_traits_view':
            full_traits_view = \
            traitsui.View((traitsui.Item("handler._full_traits_list",show_label=False)),
            title='Edit XMLDataSetWriter properties', scrollable=True, resizable=True,
            handler=TVTKBaseHandler,
            buttons=['OK', 'Cancel'])
            return full_traits_view
        elif name == 'view':
            view = \
            traitsui.View((['encode_appended_data'], ['byte_order', 'data_mode',
            'id_type'], ['block_size', 'file_name', 'number_of_time_steps',
            'time_step', 'time_step_range']),
            title='Edit XMLDataSetWriter properties', scrollable=True, resizable=True,
            handler=TVTKBaseHandler,
            buttons=['OK', 'Cancel'])
            return view
        elif name in (None, 'traits_view'):
            traits_view = \
            traitsui.View((traitsui.HGroup(traitsui.spring, "handler.view_type", show_border=True), 
            traitsui.Item("handler.info.object", editor = traitsui.InstanceEditor(view_name="handler.view"), style = "custom", show_label=False)),
            title='Edit XMLDataSetWriter properties', scrollable=True, resizable=True,
            handler=TVTKBaseHandler,
            buttons=['OK', 'Cancel'])
            return traits_view
            
