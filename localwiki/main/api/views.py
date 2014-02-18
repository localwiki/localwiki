class AllowFieldLimitingMixin(object):
    """
    A mixin for a generic APIView that will allow the serialized fields to be
    limited to a set of comma-separated values, specified via the `fields`
    query parameter.  This will only apply to GET requests.
    """
    _serializer_class_for_fields = {}

    def get_serializer_class_for_fields(self, serializer_class, fields):
        fields = fields.strip().split(',')
        fields.sort()
        fields = tuple(fields)
        if fields in self._serializer_class_for_fields:
            return self._serializer_class_for_fields[fields]
        # Doing this because a simple copy.copy() doesn't work here.
        meta = type('Meta', (serializer_class.Meta, object), {'fields': fields})
        LimitedFieldsSerializer = type('LimitedFieldsSerializer', (serializer_class,),
            {'Meta': meta})
        self._serializer_class_for_fields[fields] = LimitedFieldsSerializer
        return LimitedFieldsSerializer

    def get_serializer_class(self):
        """
        Allow the `fields` query parameter to limit the returned fields
        in list and detail views.  `fields` takes a comma-separated list of
        fields.
        """
        serializer_class = super(AllowFieldLimitingMixin, self).get_serializer_class()
        fields = self.request.QUERY_PARAMS.get('fields')
        if self.request.method == 'GET' and fields:
            return self.get_serializer_class_for_fields(serializer_class, fields)
        return serializer_class

