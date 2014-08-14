from django.shortcuts import render, redirect
from django.http import HttpResponse
import os
from comp_poster import forms
import urllib, cStringIO
from comp_poster.utils import general
from django.core.files.storage import default_storage as storage
from PIL import Image
def overlay(request):
	if request.method == 'POST':
		form = forms.CropForm(request.POST, request.FILES)
		if form.is_valid():
			x = form.cleaned_data.get('x')
			y = form.cleaned_data.get('y')	
			w = form.cleaned_data.get('w')
			h = form.cleaned_data.get('h')
			image = form.cleaned_data.get('image')
			image_file = cStringIO.StringIO(image.read())
			background = Image.open(image_file)

			#background = Image.open(os.path.join(os.getcwd(), 'pics', 'bg.png'))

			# sizes we have overlays for
			sizes = [200, 250, 300, 350, 400, 450, 500, 550, 600]

			size = general.round_down(w, sizes)
			
			#URL = 'http://4.bp.blogspot.com/-2T2XNIbAZ-s/T5-zfAjO_gI/AAAAAAAAINc/CBk42qEJPeQ/s1600/people.jpg'
			#file_from_url = cStringIO.StringIO(urllib.urlopen(URL).read())

			#background = Image.open(file_from_url).convert('RGB').crop((x, y, x+w, y+h)).resize((size,size), Image.ANTIALIAS)
			background = background.convert('RGB').crop((x, y, x+w, y+h)).resize((size,size), Image.ANTIALIAS)
			foreground = Image.open(storage.open(u'/overlays/{}.png'.format(size), 'r'))

			background.paste(foreground, (0, 0), foreground)
			#background.save(os.path.join(os.getcwd(), 'pics', 'new.png'), "PNG")
			output = cStringIO.StringIO()
			background.save(output, "PNG")
			content = output.getvalue()
			output.close()

			response = HttpResponse(content, content_type='image/png')
			response['Content-Length'] = len(content)
			response['Content-Disposition'] = 'filename="comp-poster.png";'
			return response
	else:
		form = forms.CropForm()

	return render(request, 'comp_poster/overlay.html', {'form': form})
