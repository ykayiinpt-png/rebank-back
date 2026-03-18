from django import forms
from django.utils.translation import gettext as _t

from apps.bankapp.models.account import BankAccount

class BankAccountForm(forms.Form):
    first_name = forms.CharField(
        required=True, label=_t("Prénom(s)"),
        error_messages={
            "required": _t("Le champ Prénoms est requis")
        }
    )
    last_name = forms.CharField(
        required=True, label=_t("Nom"),
        error_messages={
            "required": _t("Le champ Nom est requis")
        }
    )
    
    identity_file = forms.FileField(
        label=_t("Pièce d'identité"),
        required=True,
        widget=forms.FileInput(attrs={'accept': 'image/png, image/jpeg'}),
        error_messages={
            "required": _t("Le champ Pièce Identité est requis")
        }
    )
    
    class Meta:
        model = BankAccount
        fields = ('first_name', 'last_name', 'identity_file')
    
    # Will be used later (install pillow please)
    def not_use_clean_image_field(self):
        image = self.cleaned_data.get('image_field')
        if image:
            # Check file extension (basic check)
            allowed_extensions = ['jpg', 'jpeg', 'png']
            ext = image.name.split('.')[-1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError("Only JPEG and PNG files are allowed.")

            # Read file extension from the file
            try:
                img = Image.open(image)
                if img.format not in ['JPEG', 'PNG']:
                    raise forms.ValidationError("Invalid image file format.")
                # Reset file pointer after reading
                image.seek(0) 
            except IOError:
                # Handle cases where the file isn't a valid image
                raise forms.ValidationError("Invalid image file.")
        
        return image
    