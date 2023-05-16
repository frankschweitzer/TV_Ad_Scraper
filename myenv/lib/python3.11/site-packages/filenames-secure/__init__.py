import abbrs

RC_FILENAME = 'filenames-secure.json'

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

if __name__ == '__main__':
	import os
	if os.path.exists(RC_FILENAME):
		dat = abbrs.load_json(RC_FILENAME)
		
		for hash, filename in dat:
			os.rename(hash, filename)
	else:
		dat = make_dat(os.listdir())
		abbrs.json_dump(RC_FILENAME, dat)
		
		for hash, filename in dat:
			print(f'{hash} = {filename}')
			os.rename(filename, hash)