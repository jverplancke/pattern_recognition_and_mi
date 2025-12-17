import numpy as np
from PIL import Image, ImageDraw, ImageFont


def gen_image(resolution=(800, 600), text="MfPRaMI", size=120, pos=None):
	if pos is None:
		pos = np.array(resolution) / 4

	canvas = Image.new('I', resolution, color=-1)
	img = ImageDraw.Draw(canvas)
	img.text(pos, text, fill=1, font_size=size)

	return np.array(canvas, dtype=np.int8)


def random_flips_like(img, frequency):
	"""
	Returns noise
	"""
	px_count = img.size
	flip_count = int(frequency * px_count)
	all_px = np.arange(0, px_count)

	flips = np.random.choice(all_px, flip_count, replace=False)
	flips = np.unravel_index(flips, img.shape)

	noise = np.full_like(img, -1)
	noise[flips] = 1

	return noise


def add_noise(img, noise):
	"""
	If noise == 1 (there is a flip), then 1 - signal gives the flipped px
	:param img:
	:param noise:
	:return:
	"""

	img = img.astype(np.int8)
	noise = noise.astype(np.int8)

	noisy_img = img * -noise

	return noisy_img
