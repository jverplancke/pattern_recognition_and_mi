import img_gen
import matplotlib

matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

plt.ion()
import mrf
import numpy as np
import time
import tqdm

if __name__ == '__main__':
	gt = img_gen.gen_image()
	freq = 0.2
	np.random.seed(123)
	noise = img_gen.random_flips_like(gt, freq)
	noisy_img = img_gen.add_noise(gt, noise)

	# region Init
	fig, ax = plt.subplots(1, 2)
	ax[0].imshow(gt)
	ax[0].set_title('Ground truth')
	ax[1].imshow(noisy_img)
	ax[1].set_title(f"Image + {int(100 * freq):d}% noise")
	# endregion

	# region Starting Point
	starting_points = [(0, 0), (217, 189), (367, 125), (385, 388)]  # xy
	imgs_denoised_ifo_sp = [mrf.optimise_local_jit(noisy_img, start=c) for c in starting_points]
	scores = [mrf.prec_recall_f1(gt, fit) for fit in imgs_denoised_ifo_sp]

	fig, ax = plt.subplots(2, 3, sharex=True, sharey=True)
	fig.suptitle('Effect of starting point')
	ax[0, 0].imshow(gt)
	ax[0, 0].set_title('Ground truth')
	ax[1, 0].imshow(noisy_img)
	ax[1, 0].set_title(f"Image + {int(100 * freq):d}% noise")
	for a, img, sp, sc in zip(ax[:, 1:].flatten(), imgs_denoised_ifo_sp, starting_points, scores):
		p, r, f1 = sc
		a.imshow(img)
		a.set_title(f"Start @ {sp}\n"
		            f"P={p:.3f}, R={r:.3f}, F1={f1:.3f}")
	# endregion

	# region Traversal order
	fig, ax = plt.subplots(2, 3, sharex=True, sharey=True)
	fig.suptitle('Effect of traversal order')
	ax[0, 0].imshow(gt)
	ax[0, 0].set_title('Ground truth')
	ax[1, 0].imshow(noisy_img)
	ax[1, 0].set_title(f"Image + {int(100 * freq):d}% noise")

	denoised_order = [mrf.optimise_local_jit(noisy_img),
	                  mrf.optimise_local_jit(noisy_img, order='V'),
	                  mrf.optimise_local_jit(noisy_img, order='D'),
	                  mrf.optimise_local_jit(noisy_img, order='random')]
	labels = ["Horizontal (along rows)",
	          "Vertical (along columns)",
	          "Diagonal",
	          "Random"]

	for a, img, label in zip(ax[:, 1:].flatten(), denoised_order, labels):
		sc = mrf.prec_recall_f1(gt, img)
		a.imshow(img)
		a.set_title(f"{label}\n"
		            f"P ={sc[0]:.3f}, R ={sc[1]:.3f}, F1 ={sc[2]:.3f}")
	# endregion

	# region Paradigm
	fig, ax = plt.subplots(2, 3, sharex=True, sharey=True)
	fig.suptitle('Effect of paradigm choice')
	ax[0, 0].imshow(gt)
	ax[0, 0].set_title('Ground truth')
	ax[1, 0].imshow(noisy_img)
	ax[1, 0].set_title(f"Image + {int(100 * freq):d}% noise")

	imgs_ifo_paradigm = [mrf.optimise_local_jit(noisy_img),
	                     mrf.optimise_global(noisy_img),
	                     mrf.optimise_local_jit(noisy_img)]

	labels = ["Local", "Global", "Local, JIT"]
	for a, img, label in zip(ax[:, 1:].flatten(), imgs_ifo_paradigm, labels):
		sc = mrf.prec_recall_f1(gt, img)
		a.imshow(img)
		a.set_title(f"{label}\n"
		            f"P ={sc[0]:.3f}, R ={sc[1]:.3f}, F1 ={sc[2]:.3f}")

	scores_local, scores_local_jit, scores_global = [], [], []
	calc_time_local, calc_time_local_jit, calc_time_global = [], [], []
	noise_levels = np.arange(0.05, 0.51, 0.05)
	for noise_level in noise_levels:
		noise = img_gen.random_flips_like(gt, noise_level)
		noisy_img2 = img_gen.add_noise(gt, noise)

		start = time.time()
		local_opt = mrf.optimise_local(noisy_img2)
		scores_local.append(mrf.prec_recall_f1(gt, local_opt))
		calc_time_local.append(time.time() - start)

		start = time.time()
		local_opt_jit = mrf.optimise_local_jit(noisy_img2)
		scores_local_jit.append(mrf.prec_recall_f1(gt, local_opt_jit))
		calc_time_local_jit.append(time.time() - start)

		start = time.time()
		global_opt = mrf.optimise_global(noisy_img2)
		scores_global.append(mrf.prec_recall_f1(gt, global_opt))
		calc_time_global.append(time.time() - start)

	scores_local = np.array(scores_local).T
	scores_local_jit = np.array(scores_local_jit).T
	scores_global = np.array(scores_global).T

	fig, ax = plt.subplots(2, 2)

	fig.suptitle('Local vs global performance')
	ax[0, 0].set_title('Precision')
	ax[0, 0].plot(noise_levels, scores_local[0], label='Local')
	ax[0, 0].plot(noise_levels, scores_local_jit[0], label='Local (JIT)')
	ax[0, 0].plot(noise_levels, scores_global[0], label='Global')
	ax[0, 0].set_ylabel('Precision')
	ax[0, 0].legend()
	ax[0, 1].set_title('Recall')
	ax[0, 1].plot(noise_levels, scores_local[1], label='Local')
	ax[0, 1].plot(noise_levels, scores_local_jit[1], label='Local (JIT)')
	ax[0, 1].plot(noise_levels, scores_global[1], label='Global')
	ax[0, 1].set_ylabel('Recall')
	ax[0, 1].legend()
	ax[1, 0].set_title('F1')
	ax[1, 0].plot(noise_levels, scores_local[2], label='Local')
	ax[1, 0].plot(noise_levels, scores_local_jit[2], label='Local (JIT)')
	ax[1, 0].plot(noise_levels, scores_global[2], label='Global')
	ax[1, 0].set_ylabel('F1')
	ax[1, 0].legend()
	ax[1, 1].set_title('Execution time (s)')
	ax[1, 1].plot(noise_levels, calc_time_local, label='Local')
	ax[1, 1].plot(noise_levels, calc_time_local_jit, label='Local (JIT)')
	ax[1, 1].plot(noise_levels, calc_time_global, label='Global')
	ax[1, 1].set_yscale('log')
	ax[1, 1].set_ylabel('Time (s)')
	ax[1, 1].legend()
	for i, a in enumerate(ax.flatten()):
		a.set_xlabel('Noise level')
		if i < 3: a.set_ylim((0, 1))
	# endregion

	# region Hyperparameter optimisation (/mapping)
	b_rng, c_rng = np.arange(0, 4 + 0.1, 0.25), np.arange(0, 4 + 0.1, 0.25)
	bs, cs = np.meshgrid(b_rng, c_rng)
	f1s = np.empty_like(bs)

	for i, (b, c) in tqdm.tqdm(enumerate(zip(bs.flatten(), cs.flatten())), total=bs.size):
		observed = mrf.optimise_local_jit(noisy_img, (1, b, c))
		_, _, f1 = mrf.prec_recall_f1(gt, observed)
		f1s[np.unravel_index(i, f1s.shape)] = f1

	fig, ax = plt.subplots(1, 1)
	data = ax.pcolormesh(b_rng, c_rng, f1s, vmin=0, vmax=1)
	ax.set_xlabel('b/a')
	ax.set_ylabel('c/a')

	fig.colorbar(data, ax=ax, extend='both', label="F1")
	# endregion

	# region Foreground Density
	gts = [img_gen.gen_image(size=s, pos=(10, 10)) for s in [80, 100, 160, 240, 300]]
	gts.extend([
		img_gen.gen_image(
			text="MfPRaMI\nIMaRPfM",
			pos=(10, 10),
			size=s)
		for s in [80, 100, 160, 240, 300]
	])
	# sort by count
	counts = [len(np.where(gt == 1)[0]) for gt in gts]
	idx = np.argsort(counts)
	counts = [counts[i] / gts[0].size for i in idx]
	gts = [gts[i] for i in idx]
	# add noise
	noise = img_gen.random_flips_like(gts[0], freq)
	noisy_imgs = [img_gen.add_noise(im, noise) for im in gts]

	# get F1
	scores = []
	for gt, im in zip(gts, noisy_imgs):
		guess = mrf.optimise_local_jit(im, (1, 2, 1))
		score = mrf.prec_recall_f1(gt, guess)
		scores.append(score)

	scores = np.array(scores).T
	fig, ax = plt.subplots(2, 2)
	ax[0, 0].set_title('Precision')
	ax[0, 0].plot(counts, scores[0])
	ax[0, 1].set_title('Recall')
	ax[0, 1].plot(counts, scores[1])
	ax[1, 0].set_title('F1')
	ax[1, 0].set_xlabel("Fraction of image that is foreground")
	ax[1, 0].plot(counts, scores[2])

	for a in ax.flatten():
		a.set_ylim((0, 1))

	fig, ax = plt.subplots(3, 1)
	ax[0].imshow(noisy_imgs[0])
	ax[1].imshow(noisy_imgs[int(len(noisy_imgs) / 2)])
	ax[2].imshow(noisy_imgs[-1])
	# endregion

	for i in plt.get_fignums():
		plt.figure(i).tight_layout()
