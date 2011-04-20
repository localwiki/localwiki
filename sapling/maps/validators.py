from django.core.exceptions import ValidationError


def validate_geometry(geom):
    if not geom.valid:
        reason = geom.valid_reason
        # Skip giving the coordinates in the error message - not useful
        # unless we highlight it on the map directly.  TODO: highlight
        # the coordinates on the map directly.
        until_coordinate = reason.find('[')
        if until_coordinate == -1:
            until_coordinate = 0
        raise ValidationError("Map error: %s." %
            reason[:until_coordinate].strip().lower()
        )
