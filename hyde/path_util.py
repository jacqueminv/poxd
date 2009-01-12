import os

class PathUtil:
	@staticmethod	
	def filter_hidden_inplace(item_list):
		if(not len(item_list)): return
		wanted = filter(lambda item: not (item.startswith('.') or item.endswith('~')), item_list)
		count = len(item_list)
		good_item_count = len(wanted)
		if(count == good_item_count): return
		item_list[:good_item_count] = wanted
		for i in range(good_item_count, count):
			item_list.pop()

	@staticmethod
	def get_path_fragment(root_dir, dir):
		current_dir = dir
		current_fragment = ''
		while (not os.path.samefile(current_dir, root_dir)):
			(current_dir, current_fragment_part) = os.path.split(current_dir)
			current_fragment = os.path.join(current_fragment_part, current_fragment)
		return current_fragment

	@staticmethod
	def mirror_dir_tree(directory, source_root, mirror_root, ignore_root = False):
		current_fragment = PathUtil.get_path_fragment(source_root, directory)
		if(not current_fragment): return mirror_root
		mirror_directory = mirror_root
		if not ignore_root:
			mirror_directory = os.path.join(mirror_root, os.path.basename(source_root))
		mirror_directory = os.path.join(mirror_directory, current_fragment)
		try:
			os.makedirs(mirror_directory)
		except:
			pass
		return mirror_directory