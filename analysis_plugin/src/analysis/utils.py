'''
    Utility functions for the analysis plugin.
'''
import inspect
import importlib

def category(category_name: str = None) -> callable:
    '''
    A decorator which adds category attribute to a function.

    Args:
        category (str): Category of the function.
    '''
    def decorator(func):
        if category_name is not None:
            func.category = category_name
        return func
    return decorator

def get_function_source(
        func: callable = None,
        category_name: str = None,
        module: object = None) -> list:
    '''
    Gets the source code of function (or functions) based on name or category.
    It looks up for the function in the specified module.

    Args:
        category (str): Category of the functions.
        func (callable): Singular function whose source code is to be returned.
        module (str): Module which will be searched. Default is `analysis.analysis_source`.

    Returns:
        list: List of source code of the functions.
    '''
    func_sources = []
    if category_name is None and func is not None:
        func_sources.append(inspect.getsource(func))
    if category_name is not None and func is None:
        if module is None:
            module = importlib.import_module('analysis.analysis_source')
        for _, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and hasattr(obj, 'category') \
                and obj.category == category_name:
                func_source = ''
                source_lines = inspect.getsourcelines(obj)[0]
                for source_line in source_lines:
                    # ignoring category decorator
                    if source_line.startswith('@category'):
                        continue
                    func_source += source_line
                func_sources.append(func_source)
    return func_sources

def list_to_string(list_instance: list) -> str:
    '''
    Converts a list to a string.

    Args:
        list_instance (list): List to be converted.

    Returns:
        str: String representation of the list.
    '''
    string = ''
    for item in list_instance:
        string += item + '\n'
    return string
