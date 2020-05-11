from wtforms.validators import ValidationError, Length


class Unique(object):
    def __init__(self, model, field, message=u'This value already exists.'):
        self.model = model
        self.field = field
        self.message = message

    def __call__(self, form, field):
        check = self.model.query.filter(self.field == field.data).first()
        if check:
            raise ValidationError(self.message)


class LengthIfExists(Length):
    def __call__(self, form, field):
        if field.data:
            return super(LengthIfExists, self).__call__(form, field)

class PhoneValidator(object):
    def __call__(self, form, field):
        pass # here we can add some rules for phone validation