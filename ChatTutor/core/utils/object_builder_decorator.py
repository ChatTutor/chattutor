def build_model_from_params(from_keys : list, model : type, is_method : bool = False):
    def decorator_func(func):
        def new_function(*args, **kwargs):
            class_obj = None
            if is_method:
                class_obj = args[0]
                args = args[1:]
            model_obj = None
            keys = from_keys
            loadedargs = []
            if len(args) >= 0:
                if isinstance(args[0], model):
                    model_obj = args[0]
                else:
                    for arg in args:
                        loadedargs = loadedargs + [arg]
            
            if model_obj is None:
                assert len(loadedargs) <= len(keys)
                
                object_dict = {}
                for i in range(len(loadedargs)):
                    object_dict[keys[i]] = loadedargs[i]
                
                for key, value in kwargs.items():
                    object_dict[key] = value
                model_obj = model(**object_dict)
            if is_method:
                func(class_obj, model_obj)
            else:
                func(model_obj)
        return new_function
    return decorator_func