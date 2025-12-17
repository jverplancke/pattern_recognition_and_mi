from numba import njit
import numpy as np
import tqdm


def get_valid_neighbours(co, shape):
	n = []
	for c in co:
		if (np.all(c > 0)
				and c[0] < shape[0]
				and c[1] < shape[1]):
			n.append(tuple(c))

	return n


@njit
def _jit_optimise_core(guess, observed, idx, a, b, c, neighbours_mx, max_iters=100):
	"""
	The JIT-compiled core logic.
	Focuses on the high-speed pixel-flipping loops.
	"""
	rows, cols = observed.shape
	history = [np.copy(guess)]  # Limited list support in Numba

	for _ in range(max_iters):
		changed = False
		for px in idx:
			# Manually unravel index for performance in JIT
			r = px % rows
			c_idx = px // rows

			# Local energy calculations
			# Current value and flipped value
			val_curr = guess[r, c_idx]
			val_alt = -val_curr

			# Energy component from observation
			energy_diff_obs = (val_alt - val_curr) * (a - c * observed[r, c_idx])

			# Energy component from neighbours
			energy_diff_neigh = 0.0
			for i in range(4):
				nr, nc = r + neighbours_mx[i, 0], c_idx + neighbours_mx[i, 1]
				if 0 <= nr < rows and 0 <= nc < cols:
					# Difference in interaction energy: -b * (alt*neigh - curr*neigh)
					energy_diff_neigh += -b * (val_alt - val_curr) * guess[nr, nc]

			if (energy_diff_obs + energy_diff_neigh) < 0:
				guess[r, c_idx] = val_alt
				changed = True

		# Convergence Check: Compare against history
		# Note: Numba handles this best with explicit array comparisons
		is_periodic = False
		for prev in history:
			if np.array_equal(guess, prev):
				is_periodic = True
				break

		if is_periodic or not changed:
			break

		history.append(np.copy(guess))

	return guess


def optimise_local_jit(observed, params=(1, 1, 1), start=(0, 0), order='H'):
	a, b, c = params

	neighbours_mx = np.array([[-1, 0], [1, 0], [0, -1], [0, 1]], dtype=np.int32)

	if order == 'V':
		observed = observed.T

	if order == 'D':
		idx = get_diagonal_raveled_indices(observed).astype(np.int64)
	else:
		idx = np.arange(observed.size, dtype=np.int64)

	if order == 'random':
		np.random.shuffle(idx)

	start_idx = start[0] + start[1] * observed.shape[1]
	idx = np.roll(idx, -start_idx)  # Roll left to start at specific index

	guess = np.copy(observed)
	result = _jit_optimise_core(guess, observed, idx, a, b, c, neighbours_mx)

	# 3. Finalize Output
	if order == 'V':
		result = result.T

	return result


def optimise_local(observed, params=(1, 1, 1), start=(0, 0), order='H'):
	a, b, c = params

	neighbours_mx = np.array([
		[-1, 0],
		[1, 0],
		[0, -1],
		[0, 1]
	])

	if order == 'V':
		observed = observed.T
		idx = np.arange(len(observed.flatten()))
	elif order == 'D':
		idx = get_diagonal_raveled_indices(observed)
	else:
		idx = np.arange(len(observed.flatten()))

	if order == 'random':
		np.random.shuffle(idx)
	start_idx = start[0] + start[1] * observed.shape[1]  # input is in xy. column + row*row length
	idx = np.roll(idx, start_idx)
	guess = np.copy(observed)

	intermediate_images = [observed]
	while True:
		for px in tqdm.tqdm(idx, total=guess.size):
			img_co = np.unravel_index(px, observed.shape, order='F')

			neighbours_co = [img_co + n for n in neighbours_mx]
			neighbours = get_valid_neighbours(neighbours_co, observed.shape)  # for loop for legibility

			# calculate energy for both possible values of x_i
			energy_curr = guess[img_co] * (a - c * observed[img_co])
			energy_alt = -guess[img_co] * (a - c * observed[img_co])
			for n in neighbours:
				energy_curr += -b * guess[img_co] * guess[n]
				energy_alt += -b * -guess[img_co] * guess[n]

			if energy_alt < energy_curr:
				guess[img_co] *= -1

		if np.any([np.all(guess == img) for img in intermediate_images]):
			# converged. Stronger condition than simply checking whether the last 2 guesses
			# were the same because we can imagine situations where there is periodicity
			# (see e.g. Conway's game of life), though this may be side-stepped somewhat by the sequential nature

			break

		intermediate_images.append(np.copy(guess))

	if order == 'V':
		guess = guess.T

	return guess


def optimise_global(observed, params=(1, 1, 1)):
	a, b, c = params

	guess = np.copy(observed)
	intermediate_images = [observed]
	i = 0
	while True:
		i += 1
		#print(f"{i} parallel iteration{"" if i == 1 else "s"}")
		energy_curr = guess * (a - c * observed)
		energy_curr[:-1] += - b * guess[:-1] * guess[1:]
		energy_curr[1:] += -b * guess[1:] * guess[:-1]
		energy_curr[:, :-1] += -b * guess[:, :-1] * guess[:, 1:]
		energy_curr[:, 1:] += -b * guess[:, 1:] * guess[:, :-1]

		# simply -energy_curr
		energy_alt = -guess * (a - c * observed)
		energy_alt[:-1] += b * guess[:-1] * guess[1:]
		energy_alt[1:] += b * guess[1:] * guess[:-1]
		energy_alt[:, :-1] += b * guess[:, :-1] * guess[:, 1:]
		energy_alt[:, 1:] += b * guess[:, 1:] * guess[:, :-1]

		# flip where appropriate
		guess[np.where(energy_alt < energy_curr)] *= -1

		if np.any([np.all(guess == img) for img in intermediate_images]):
			# converged. Stronger condition than simply checking whether the last 2 guesses
			# were the same because we can imagine situations where there is periodicity
			# (see e.g. Conway's game of life), though this may be side-stepped somewhat by the sequential nature

			break

		intermediate_images.append(np.copy(guess))
	return guess


def error(original, denoised):
	pos_gt = set(list(np.where(original.ravel() == 1)[0]))
	neg_gt = set(list(np.where(original.ravel() == -1)[0]))
	pos_opt = set(list(np.where(denoised.ravel() == 1)[0]))
	neg_opt = set(list(np.where(denoised.ravel() == -1)[0]))

	tp = len(pos_gt.intersection(pos_opt))
	tn = len(neg_gt.intersection(neg_opt))
	fp = len(pos_opt.intersection(neg_gt))
	fn = len(neg_opt.intersection(pos_gt))

	return tp, tn, fp, fn


def prec_recall_f1(gt, opt):
	tp, tn, fp, fn = error(gt, opt)
	precision = tp / (tp + fp) if tp + fp != 0 else 0
	recall = tp / (tp + fn) if tp + fn != 0 else 0
	f1 = 2 * precision * recall / (precision + recall) if precision + recall != 0 else 0

	return precision, recall, f1


def get_diagonal_raveled_indices(matrix):
	row_idx, col_idx = np.indices(matrix.shape)

	# Elements on the same anti-diagonal share the same (row + col)
	diagonal_sums = row_idx + col_idx

	raveled_indices = np.lexsort((row_idx.ravel(), diagonal_sums.ravel()))
	return raveled_indices
