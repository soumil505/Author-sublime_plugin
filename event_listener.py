import sublime,sublime_plugin
import re,os,json

def find_mistakes(view,wordlist):
	string=view.substr(view.word(sublime.Region(0,1000000)))
	words_full=re.split(r"[\"\.,\?!@#$%&\*\(\)~`/\\<>\[\]{}:;\-\+\n\s\b ]",string)
	# print(words_full)
	words_full=[w for w in words_full if words_full.count(w)<3 and len(w)!=0 and not re.match(r"[0-9]+$",w)]
	mistakes=list(set([w for w in words_full if w not in wordlist]))
	# print(mistakes)
	regions=[]
	for m in mistakes:
		regions+=view.find_all("\\b"+m+"\\b")
	# print(regions)
	view.add_regions("mistake",regions,"mistake",icon="Packages/Author/mistake.png",flags=sublime.DRAW_SQUIGGLY_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE)

class EventListener(sublime_plugin.ViewEventListener):
	
	def on_post_save(self):
		if "text.author" not in self.view.scope_name(self.view.sel()[0].begin()).split():
			return
		settings=self.view.settings()
		settings.set("color_scheme", "author.sublime-color-scheme")

	def on_modified_async(self):
		if "text.author" not in self.view.scope_name(self.view.sel()[0].begin()).split():
			return
		wordlist2=json.load(open(os.path.join(sublime.packages_path(),"Author/dict.json"),"r"))
		find_mistakes(self.view,wordlist2)
		loc=self.view.sel()[0].begin()
		string=self.view.substr(self.view.word(sublime.Region(loc-35,loc)))
		words_full=re.split(r"[\"\.,\?!@#$%&\*\(\)~`/\\<>\[\]{}:;\-\+\n\s\b ]",string)
		#TODO add some sort of scoring system for relevency
		if len(words_full)>1:
			words=words_full[1:-1]
		else:
			words=[]
		try:
			self.wordlist=self.wordlist.union(set([w.lower() for w in words]))
		except:
			# print("here")
			string2=self.view.substr(self.view.word(sublime.Region(0,1e7)))
			words2=re.split(r"[\"\.,\?!@#$%&\*\(\)~`/\\<>\[\]{}:;\-\+\n\s\b ]",string2)
			words2=[w.lower() for w in words2 if re.match(r"^[A-Z]",w) or len(w)>4]
			self.wordlist=set(words2)
		# print(self.wordlist)
		prefix=words_full[-1]
		if prefix=="":
			return
		try:
			if self.use_dict:
				wordlist=wordlist2
			else:
				wordlist=list(self.wordlist)
		except:
			self.use_dict=False
			wordlist=list(self.wordlist)
		matches=[w for w in wordlist if w[:len(prefix)]==prefix.lower()]
		if prefix[0]==prefix[0].upper():
			matches=[m[0].upper()+m[1:] for m in matches]
		# print(prefix,matches,self.wordlist)
		if len(matches)==0:
			return
		if len(matches)>50:
			matches=matches[:50]
		
		self.curr_matches=matches
		self.auto_html="""<style> div.highlight0 {background-color: #555;padding: 2px;}</style>"""
		self.autocomplete_index=0
		self.autocomplete_index_cap=len(matches)
		self.auto_html+="<br>".join(["<div class=\"highlight"+str(style)+"\">"+"<a href='"+word+"'>"+word+"</a></div>" for style,word in enumerate(matches)])
		self.view.show_popup(self.auto_html,sublime.HIDE_ON_MOUSE_MOVE_AWAY or sublime.COOPERATE_WITH_AUTO_COMPLETE,loc,
			on_navigate=lambda s:[self.view.run_command("delete_word",{"forward":False}),self.view.run_command("overwrite",{"characters":s})])
		# self.view.show_popup_menu(list(self.wordlist),lambda x:print(x))
	def on_text_command(self,command,args):
		# print(command)
		if command=="set_file_type":
			# print(args)
			if "author" in re.split(r"[/\.]",args["syntax"]):
				settings=self.view.settings()
				settings.set("color_scheme", "author.sublime-color-scheme")
		if "text.author" not in self.view.scope_name(self.view.sel()[0].begin()).split():
			return
		
		in_popup=False
		if command=="up_placeholder":
			try:
				self.autocomplete_index-=1
				self.autocomplete_index=self.autocomplete_index%self.autocomplete_index_cap
			except:
				self.autocomplete_index=0
			in_popup=True
		if command=="down_placeholder":
			try:
				self.autocomplete_index+=1
				self.autocomplete_index=self.autocomplete_index%self.autocomplete_index_cap
			except:
				self.autocomplete_index=0
			in_popup=True
		if command=="enter_placeholder":
			[self.view.run_command("delete_word",{"forward":False}),self.view.run_command("overwrite",{"characters":self.curr_matches[self.autocomplete_index]})]
			in_popup=True
		if command=="right_placeholder":
			# print("here")
			try:
				self.use_dict=not self.use_dict
			except:
				self.use_dict=False
			self.on_modified_async()
			in_popup=True
		if command=="autocomplete_mode_toggle":
			# print("here")
			try:
				self.use_dict=not self.use_dict
			except:
				self.use_dict=False
			self.on_modified_async()
		if in_popup:
			self.auto_html="""<style> div.highlight"""+str(self.autocomplete_index)+""" {background-color: #555;padding: 2px;}</style>"""+self.auto_html.split("</style>")[1]
			self.view.update_popup(self.auto_html)
			# print(self.autocomplete_index,self.auto_html)