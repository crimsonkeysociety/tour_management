from django import forms
from comp_poster import models

class CropForm(forms.Form):
	x = forms.IntegerField(max_value=9999, required=True)
	y = forms.IntegerField(max_value=9999, required=True)
	w = forms.IntegerField(max_value=9999, required=True)
	h = forms.IntegerField(max_value=9999, required=True)
	image = forms.ImageField()