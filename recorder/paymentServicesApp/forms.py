from django import forms


PERIOD_CHOICE = (
    ('1', 'One Month'),
    ('3', 'Three Month'),
    ('12', 'Twelve Month'),
)


class ChoicePeriodOfSubscriptionForm(forms.Form):

    period = forms.ChoiceField(choices=PERIOD_CHOICE, widget=forms.RadioSelect(attrs={
        'id': 'RadioSelectBTNS'
    }))
