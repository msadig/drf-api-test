
class MultiSerializerViewSetMixin:
    '''
        For using different serializers for different request types
        credit: http://stackoverflow.com/q/22616973
    '''
    serializer_classes = {
        'default': None,
    }

    def __init__(self, *args, **kwargs):
        """Make sure initialized instance has required attrs

        Raises:
            AttributeError: if there's no any default serializer defined
        """

        if hasattr(self, "serializer_class"):
            if self.serializer_classes['default'] is None:
                raise AttributeError(
                    "{} object has no default serializer defined for multi-serializer!".format(
                        type(self),
                    )
                )

    def get_serializer_class(self):
        """Gets serialzer based on action type.

        To learn about available actions on viewsets: 
            * https://www.django-rest-framework.org/api-guide/viewsets/#viewset-actions

        Returns:
            Serializer: matching serializer to action, otherwise default serializer
        """
        try:
            return self.serializer_classes.get(
                self.action,
                self.serializer_classes['default']
            )
        except Exception as exc:
            return super().get_serializer_class()
