def build_model_from_params(from_keys: list, model: type, is_method: bool = False):
    """Makes definition of model params functions easier.
    Use as such:
        ```python
        class Model:
            p1 : str
            p2 : str

        class DB:
            @build_model_from_params(from_keys=["p1", "p2"], model=Model, is_method=True)
            def create(self, *args, **kwargs):
                ... # args[0] will be of type Model
                do_something(args[0])
        [...]

        # Calling the function
        DB.create(p1=2, p2=3)
        # or
        DB.create(2, 3)
        # or
        DB.create(2, p2=3)
        # or
        Model model = Model(2, 3)
        DB.create(model)
        ```
    When using outside a class, is_method should be false.

    Args:
        from_keys (list): keys of the Model class
        model (type): Model class
        is_method (bool, optional): Weather the decorated obj is a
            function of a method inside a class. Defaults to False.
    """

    def decorator_func(func):
        def new_function(*args, **kwargs):
            class_obj = None
            if is_method:
                class_obj = args[0]
                args = args[1:]
            model_obj = None
            keys = from_keys
            loadedargs = []
            if len(args) > 0:
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
                return func(class_obj, model_obj)
            else:
                return func(model_obj)

        return new_function

    return decorator_func
