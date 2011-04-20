from django import forms


class DeleteForm(forms.Form):
    comment = forms.CharField(max_length=150, required=False,
        label="Reason for deletion")


class RevertForm(forms.Form):
    comment = forms.CharField(max_length=150, required=False,
        label="Reason for revert")
