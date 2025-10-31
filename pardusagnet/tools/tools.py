import inspect
from docstring_parser import parse

class Tool:
    def __init__(self, func:callable):
        self.func:callable = func
    
    def _get_schema(
        self,
        descriptions: dict[str , str] = {},
        required: list[str] = []
    ):
        sig = inspect.signature(self.func)
        all_params = list(sig.parameters.keys())
        
        # Get annotations excluding 'return' type annotation
        param_annotations = {
            param: annot 
            for param, annot in self.func.__annotations__.items() 
            if param != 'return'
        }
        
        if len(all_params) != len(param_annotations):
            raise KeyError("All parameters must be annotated")

        string_annotations = {
            param: class_type.__name__
            for param, class_type in param_annotations.items()
        }

        properties = {}
        for params in all_params:
            properties[params] = {
                "type": string_annotations[params],
                "description": descriptions.get(params, ""),
            }

        return {
            "type":"function",
            "name":self.func.__name__,
            "description":self.func.__doc__,
            "parameters":{
                "type":"object",
                "properties":properties
            },
            "required":required,
            "additionalProperties":False
        }


