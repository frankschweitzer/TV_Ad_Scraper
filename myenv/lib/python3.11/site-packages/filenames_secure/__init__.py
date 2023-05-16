import os
import abbrs

def current_path():
	p = os.path.realpath(__file__)
	p = os.path.split(p)[0]
	p = os.path.split(p)[-1]
	return p

PACKAGE_NAME = current_path()
RC_FILENAME = f'{PACKAGE_NAME}.json'

def make_dat(ls):
	def is_mp4(x):
		s = x.split('.')
		return len(s) >= 2 and (s[-1] == 'mp4' or s[-2] == 'mp4')

	def check_collision(d):
		for i, v in enumerate(d):
			for j in range(i + 1, len(d)):
				if d[i][0] == d[j][0]:
					return j
	
	dat = [ [ abbrs.cool_hash(i), i ] for i in filter(is_mp4, ls) ]
	
	while True:
		i = check_collision(dat)
		if i:
			print(f'Repairing collision: {dat[i][0]} -> {dat[i][1]}')
			dat[i][0] = abbrs.cool_hash(dat[i][0])
		else:
			break
	
	return dat

def restore():
	dat = abbrs.load_json(RC_FILENAME)
	for hash, filename in dat:
		os.rename(hash, filename)
	abbrs.suspend_file(RC_FILENAME)

def secure():
	dat = make_dat(os.listdir())
	if len(dat) == 0:
		print('MP4 files not found.')
		return

	abbrs.json_dump(RC_FILENAME, dat)
	print(abbrs.table([ 'Hash', 'Filename' ], dat))
	for hash, filename in dat:
		os.rename(filename, hash)

def main():
	if os.path.exists(RC_FILENAME):
		restore()
	else:
		secure()

if __name__ == '__main__':
	main()