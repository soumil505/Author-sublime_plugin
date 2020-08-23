import sublime
import sublime_plugin
import urllib
import threading
import re
import os
import json


class WrapChapterCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		view=self.view
		window=view.window()
		settings=view.settings()
		
		selectors=view.find_by_selector("chapter_keyword")
		chapter_content=[]
		print(selectors)
		for i in range(len(selectors)-1):
			i=len(selectors)-i-1
			chapter_content.append(selectors[i].cover(selectors[i-1]))
		# print(chapter_content)
		current=view.sel()[0]
		# print(view.scope_name(current.begin()).split())
		if "chapter_keyword" in view.scope_name(current.begin()).split():
			current=sublime.Region(current.begin()+7,current.end()+7)
		for region in chapter_content:
			if region.intersects(current):
				# print(region)
				view.fold(sublime.Region(region.begin()+7,region.end()))
				
class UpPlaceholderCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		pass
		
class DownPlaceholderCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		pass
		
class EnterPlaceholderCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		pass

class RightPlaceholderCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		pass

class AutocompleteModeToggleCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		pass

class DefineCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		loc=self.view.sel()[0].begin()
		string=self.view.substr(self.view.word(sublime.Region(loc-1,loc)))
		self.view.show_popup("Awaiting response for : "+string,
			sublime.HIDE_ON_MOUSE_MOVE_AWAY or sublime.COOPERATE_WITH_AUTO_COMPLETE,self.view.line(loc).begin(),1000)
		thread=DefineRequest(self.view,string,5)
		thread.start()

class DefineRequest(threading.Thread):
	def __init__(self, view, string, timeout):
		self.view = view
		self.word = string
		self.timeout = timeout
		self.result = None
		threading.Thread.__init__(self)
 
	def run(self):
		try:
			response = urllib.request.urlopen('https://www.dictionary.com/browse/'+self.word,timeout=self.timeout)
			html = response.read().decode()
			def unencode(match):
				st=match.group(0)
				return chr(int(st[3:-1],16))
			html=re.sub(r"&#.{0,4}?;",unencode,html)
			defs=re.findall(r"<div value=\".*?</div>",html)
			print(defs)
			self.view.update_popup("<h1>{}</h1>".format(self.word)+"<br>".join(defs))
		except urllib.error.HTTPError as e:
			response=urllib.request.urlopen('https://www.wordhippo.com/what-is/another-word-for/'+self.word+".html",timeout=self.timeout)
			html=response.read().decode()
			words=re.findall(r"<div class=\"wordblock.*?</div>",html)
			# print(html)
			print(words)
			self.view.update_popup("<h1>No results for {}</h1><br>Did you mean:<br>".format(self.word)+"<br>".join(words).replace("<a","<div").replace("</a","</div"))
		
class ThesaurusCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		loc=self.view.sel()[0].begin()
		string=self.view.substr(self.view.word(sublime.Region(loc-1,loc)))
		self.view.show_popup("Awaiting response for : "+string,
			sublime.HIDE_ON_MOUSE_MOVE_AWAY or sublime.COOPERATE_WITH_AUTO_COMPLETE,self.view.line(loc).begin(),1000)
		thread=ThesaurusRequest(self.view,string,5)
		thread.start()

class ThesaurusRequest(threading.Thread):
	def __init__(self, view, string, timeout):
		self.view = view
		self.word = string
		self.timeout = timeout
		self.result = None
		threading.Thread.__init__(self)
 
	def run(self):
		try:
			response = urllib.request.urlopen('https://www.thesaurus.com/browse/'+self.word,timeout=self.timeout)
			html = response.read().decode()
			words=re.search(r"Synonyms for(.*?)MOST RELEVANT",html).group(1)
			words=re.sub(r"</?.*?>","  ",words)
			def unencode(match):
				st=match.group(0)
				return chr(int(st[3:-1],16))
			words=re.sub(r"&#.{0,4}?;",unencode,words)
			print(words)
			self.view.update_popup("<h1>{}</h1>".format(self.word)+words)
		except urllib.error.HTTPError as e:
			response=urllib.request.urlopen('https://www.wordhippo.com/what-is/another-word-for/'+self.word+".html",timeout=self.timeout)
			html=response.read().decode()
			words=re.findall(r"<div class=\"wordblock.*?</div>",html)
			# print(html)
			print(words)
			self.view.update_popup("<h1>No results for {}</h1><br>Did you mean:<br>".format(self.word)+"<br>".join(words).replace("<a","<div").replace("</a","</div")+"<br>")

class AutoCorrectCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		words=json.load(open(os.path.join(sublime.packages_path(),"Author/dict.json"),"r"))
		loc=self.view.sel()[0].begin()
		string=self.view.substr(self.view.word(sublime.Region(loc-1,loc)))
		csum=lambda s:sum([ord(x) for x in s])
		def isin(a,b):
			for c in a:
				if c not in b:
					return False
			return True
		matches=[w for w in words if w[0]==string[0] and abs(len(w)-len(string))<=3 and (isin(string,w) or isin(w,string))]

		print(matches)
		def editDistance(str1, str2, m, n): 
			if m == 0: 
				 return n
			if n == 0: 
				return m
			if str1[m-1]== str2[n-1]: 
				return editDistance(str1, str2, m-1, n-1) 
			return 1 + min(editDistance(str1, str2, m, n-1),
						   editDistance(str1, str2, m-1, n),
						   editDistance(str1, str2, m-1, n-1))
		dist=[editDistance(m,string,len(m),len(string)) for m in matches]
		matches=[x for d,x in sorted(zip(dist,matches)) if d<=3]
		window=self.view.window()
		window.status_message(str(len(matches))+" match(es) found")
		if len(matches)>50:
			matches=matches[:50]
		def done(s):
			if s!=-1:
				self.view.run_command("delete_word",{"forward":False})
				self.view.run_command("overwrite",{"characters":matches[s]})
		self.view.show_popup_menu(matches,done)
		
