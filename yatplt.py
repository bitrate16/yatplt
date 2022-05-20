"""
MIT License

Copyright (c) 2022 bitrate16

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
"""
Copyright 2022 bitrate16

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import ast
import dis
import typing
import asyncio
import os


# Default values for block syntax
# One-time block that is called during .init() call before template is rendered
ONE_TIME_BLOCK_START = '{1{!'
"""
One-time expression that is evaluated during .init() call before template is 
rendered. This block has no result and is removed from resulting render.

Defines block start

Example:
```
{1{!
def useful_function(something):
	return something + ' is useful'
!}1}
```
"""
ONE_TIME_BLOCK_END   = '!}1}'
"""
One-time expression that is evaluated during .init() call before template is 
rendered. This block has no result and is removed from resulting render.

Defines block end

Example:
```
{1{!
def useful_function(something):
	return something + ' is useful'
!}1}
"""

ONE_TIME_EXPRESSION_START = '{1{%'
"""
One-time expression that is evaluated during .init() call before template is 
rendered. Expression result is inserted into the final template instead of this 
expression block.

Defines block start

Example:
```
{1{%
useful_function('my shitcode')
%}1}
"""
ONE_TIME_EXPRESSION_END   = '%}1}'
"""
One-time expression that is evaluated during .init() call before template is 
rendered. Expression result is inserted into the final template instead of this 
expression block.

Defines block end

Example:
```
{1{%
useful_function('my shitcode')
%}1}
"""

COMMENT_BLOCK_START = '{{#'
"""
Defines comment block that is entirely deleted from resulting render including 
block content.

Defines block start

Example:
```
{{#
def not_useful_function(something):
	return something + ' is NOT useful'

log(not_useful_function('my code'))
#}}
"""
COMMENT_BLOCK_END = '#}}'
"""
Defines comment block that is entirely deleted from resulting render including 
block content.

Defines block end

Example:
```
{{#
def not_useful_function(something):
	return something + ' is NOT useful'

log(not_useful_function('my code'))
#}}
"""

BLOCK_START = '{{!'
"""
Renderable expression that is evaluated during .render() call before template is 
rendered. This block has no result and is removed from resulting render.

Defines block start

Example:
```
{1{!
total_usefulness = 0
!}1}

{{!

def useful_function(something):
	total_usefulness += 1
	return something + ' is useful ' + total_usefulness + ' times
!}}
```
"""
BLOCK_END   = '!}}'
"""
Renderable expression that is evaluated during .render() call before template is 
rendered. This block has no result and is removed from resulting render.

Defines block end

Example:
```
{1{!
total_usefulness = 0
!}1}

{{!

def useful_function(something):
	total_usefulness += 1
	return something + ' is useful ' + total_usefulness + ' times
!}}
"""

EXPRESSION_START = '{{%'
"""
Renderable expression that is evaluated during .render() call before template is 
rendered. Expression result is inserted into the final result instead of this 
expression block.

Defines block start

Example:
```
{{%
useful_function('my shitcode')
%}}
"""
EXPRESSION_END   = '%}}'
"""
Renderable expression that is evaluated during .render() call before template is 
rendered. Expression result is inserted into the final result instead of this 
expression block.

Defines block end

Example:
```
{{%
useful_function('my shitcode')
%}}
"""


def findall(s: str, sub: str, ind: int=0):
	"""
	Find all ocurrencies for sub in s starting from ind
	"""
	
	ind = s.find(sub, ind)
	while ind != -1:
		yield ind
		ind = s.find(sub, ind + 1)


def classenum(l: list, clazz: int):
	"""
	zip(l, [clazz]*len(l))
	"""
	
	return list(zip(l, [ clazz ] * len(l)))


def countsameleft(s: str, c: str):
	"""
	Count same characters from left
	"""
	
	count = 0
	while s[count] == c:
		count += 1
	
	return count


def autotablete(code: str):
	"""
	Remove excessive tabs/spaces by finding minimal ident.
	
	Example:
	"""
	
	# I don't care about cookies
	split_lines = code.split('\n')
	lines = []
	for line in split_lines:
		if len(line.strip()):
			lines.append(line.rstrip())
	
	# Skip empty
	if len(lines) == 0 or len(lines[0]) == 0:
		return code
	
	# Skip noident
	if lines[0][0] != '\t' and lines[0][0] != ' ':
		return code
	
	ident_char = lines[0][0]
	min_ident = countsameleft(lines[0], ident_char)
	
	# Remove excessive ident from each line
	for i, line in enumerate(lines):
		if countsameleft(line, ident_char) < min_ident:
			raise SyntaxError('Ident of the first line does not match ident of the other lines')
		
		lines[i] = line[min_ident:]
	
	return '\n'.join(lines)


class TemplateFragment:
	"""
	Represnts single fragment of the templste
	"""
	
	def __init__(self):
		pass
	
	def is_one_time(self) -> bool:
		"""
		Returns True if this fragment is one-pass type and executed inside 
		Template.init()
		"""
		
		return False
	
	async def render(self, context: dict, scope: dict) -> typing.Union[str, typing.Awaitable[str]]:
		"""
		Renders the given fragment inside given context with passed arguemnts.
		
		context is single for entire template and holds all values between 
		.render() calls.
		
		scope is unique dict per each call of .render().
		
		Expected result of .render() call is string or coroutine returning 
		string.
		"""
		
		return None


class StringTemplateFragment(TemplateFragment):
	"""
	Represents single template fragment containing plain string value
	"""
	
	def __init__(self, value: str):
		super().__init__()
		self.value = value
	
	def is_one_time(self) -> bool:
		return False
	
	async def render(self, context: dict, scope: dict) -> typing.Union[str, typing.Awaitable[str]]:
		return self.value
	
	def __str__(self):
		return self.value
	
	def __repr__(self):
		return self.value


class ExpressionTemplateFragment(TemplateFragment):
	"""
	Represents single template fragment containing executable expression that 
	supports eval(). Can contain both: one pass and multiple pass expressions
	"""
	
	def __init__(self, source_string: str, one_time: bool = False,	expression_start_tag: str=None, 
																	expression_end_tag: str=None,
																	save_source: bool=True,
																	_tag_index: int=None):
		super().__init__()
		file_name = '<ExpressionTemplateFragment>' if _tag_index is None else f'<ExpressionTemplateFragment_{_tag_index}>'
		self.evaluable = compile(autotablete(source_string), file_name, 'eval', flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
		self.one_time = one_time
		self.expression_start_tag = expression_start_tag or (ONE_TIME_EXPRESSION_START if self.one_time else EXPRESSION_START)
		self.expression_end_tag = expression_end_tag or (ONE_TIME_EXPRESSION_END if self.one_time else EXPRESSION_START)
		self.source_string = source_string if save_source else None
	
	def is_one_time(self) -> bool:
		return self.one_time
	
	async def render(self, context: dict, scope: dict) -> typing.Union[str, typing.Awaitable[str]]:
		result = eval(self.evaluable, context, scope)
		
		if asyncio.iscoroutine(result):
			return await result
		
		return result
	
	def __str__(self):
		if self.source_string is None:
			return f'{self.expression_start_tag}\n{dis.dis(self.evaluable)}\n{self.expression_end_tag}'
		else:
			return f'{self.expression_start_tag}\n{self.source_string}\n{self.expression_end_tag}'
	
	def __repr__(self):
		if self.source_string is None:
			return f'{self.expression_start_tag}\n{dis.dis(self.evaluable)}\n{self.expression_end_tag}'
		else:
			return f'{self.expression_start_tag}\n{self.source_string}\n{self.expression_end_tag}'


class BlockTemplateFragment(TemplateFragment):
	"""
	Represents single template fragment containing executable code block that 
	supports exec()/eval(). Can contain both: one pass and multiple pass 
	expressions
	"""
	
	def __init__(self, source_string: str, one_time: bool = False,	block_start_tag: str=None, 
																	block_end_tag: str=None,
																	save_source: bool=True,
																	_tag_index: int=None):
		super().__init__()
		file_name = '<BlockTemplateFragment>' if _tag_index is None else f'<BlockTemplateFragment{_tag_index}>'
		self.executable = compile(autotablete(source_string), file_name, 'exec', flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
		self.one_time = one_time
		self.block_start_tag = block_start_tag or (ONE_TIME_BLOCK_START if self.one_time else BLOCK_START)
		self.block_end_tag = block_end_tag or (ONE_TIME_BLOCK_END if self.one_time else BLOCK_START)
		self.source_string = source_string if save_source else None
	
	def is_one_time(self) -> bool:
		return self.one_time
	
	async def render(self, context: dict, scope: dict) -> typing.Union[str, typing.Awaitable[str]]:
		result = eval(self.executable, context, scope)
		if asyncio.iscoroutine(result):
			await result
		return None
	
	def __str__(self):
		if self.source_string is None:
			return f'{self.block_start_tag}\n{dis.dis(self.executable)}\n{self.block_end_tag}'
		else:
			return f'{self.block_start_tag}\n{self.source_string}\n{self.block_end_tag}'
	
	def __repr__(self):
		if self.source_string is None:
			return f'{self.block_start_tag}\n{dis.dis(self.executable)}\n{self.block_end_tag}'
		else:
			return f'{self.block_start_tag}\n{self.source_string}\n{self.block_end_tag}'


class TemplateParser:
	"""
	Utility class that provides template parsing funtionality.
	
	Entire set of parameters for tag start and end literals match their 
	description for defualt defined values.
	
	`strip_string` sets string trim() mode. If set to True, each part of string 
	not in code blocks is stripped to remove excessive spaces.
	
	`save_source_string` enables parser to save source code inside TemplateFragment so 
	it can be printed later.
	"""
	
	def __init__(self, one_time_block_start: str=ONE_TIME_BLOCK_START, 
						one_time_block_end: str=ONE_TIME_BLOCK_END,
						one_time_expression_start: str=ONE_TIME_EXPRESSION_START,
						one_time_expression_end: str=ONE_TIME_EXPRESSION_END,
						comment_block_start: str=COMMENT_BLOCK_START,
						comment_block_end: str=COMMENT_BLOCK_END,
						block_start: str=BLOCK_START,
						block_end: str=BLOCK_END,
						expression_start: str=EXPRESSION_START,
						expression_end: str=EXPRESSION_END,
						strip_string: bool=True,
						save_source_string: bool=True):
		
		self.one_time_block_start      = one_time_block_start     
		self.one_time_block_end        = one_time_block_end       
		self.one_time_expression_start = one_time_expression_start
		self.one_time_expression_end   = one_time_expression_end  
		self.comment_block_start       = comment_block_start      
		self.comment_block_end         = comment_block_end        
		self.block_start               = block_start              
		self.block_end                 = block_end                
		self.expression_start          = expression_start         
		self.expression_end            = expression_end           
		
		self.save_source_string      = save_source_string
		self.strip_string            = strip_string
	
	def parse(self, source: str):
		"""
		Perform parsing of the given source and returns list of pseudo-tokens
		"""
		
		
		# ---> First pass: remove comments
		
		
		comment_start = classenum(list(findall(source, self.comment_block_start)), 0)
		comment_end = classenum(list(findall(source, self.comment_block_end)), 1)
		
		if len(comment_start) < len(comment_end):
			raise RuntimeError(f'{self.comment_block_start} and {self.comment_block_end} tags count mismatch: {len(comment_start)} != {len(comment_end)}')
		
		ordered_comment_tags = sorted(comment_start + comment_end, key=lambda x: x[0])
		
		# Iterate over all comment open/close tags and remove these intervals from input data
		if len(ordered_comment_tags):
			
			cursor = 0
			
			while cursor < len(ordered_comment_tags):
				
				# Cound closing tag before opening tag
				if ordered_comment_tags[cursor][1] == 1:
					raise RuntimeError(f'Unmatched {self.comment_block_end} tag')
				
				comment_start_index = ordered_comment_tags[cursor][0]
				
				# Find closest closing tag
				while True:
					if cursor >= len(ordered_comment_tags):
						raise RuntimeError(f'Unmatched {self.comment_block_start} tag')
					
					if ordered_comment_tags[cursor][1] == 1:
						break
					
					cursor += 1
				
				source = source[:comment_start_index] + source[ordered_comment_tags[cursor][0] + len(COMMENT_BLOCK_END):]
				cursor += 1
		
		
		# ---> Second pass: parse all tags and sort list
		
		
		tag_by_id = [
			self.one_time_block_start,
			self.one_time_block_end,
			self.one_time_expression_start,
			self.one_time_expression_end,
			self.block_start,
			self.block_end,
			self.expression_start,
			self.expression_end
		]
		
		one_time_block_start      = classenum(list(findall(source, self.one_time_block_start)), 0)
		one_time_block_end        = classenum(list(findall(source, self.one_time_block_end)), 1)
		one_time_expression_start = classenum(list(findall(source, self.one_time_expression_start)), 2)
		one_time_expression_end   = classenum(list(findall(source, self.one_time_expression_end)), 3)
		block_start               = classenum(list(findall(source, self.block_start)), 4)
		block_end                 = classenum(list(findall(source, self.block_end)), 5)
		expression_start          = classenum(list(findall(source, self.expression_start)), 6)
		expression_end            = classenum(list(findall(source, self.expression_end)), 7)
		
		# Complimentary check
		if len(one_time_block_start) != len(one_time_block_end):
			raise RuntimeError(f'{self.one_time_block_start} and {self.one_time_block_end} tags count mismatch: {len(one_time_block_start)} != {len(one_time_block_end)}')
			
		if len(one_time_expression_start) != len(one_time_expression_end):
			raise RuntimeError(f'{self.one_time_expression_start} and {self.one_time_expression_end} tags count mismatch: {len(one_time_expression_start)} != {len(one_time_expression_end)}')
			
		if len(block_start) != len(block_end):
			raise RuntimeError(f'{self.block_start} and {self.block_end} tags count mismatch: {len(block_start)} != {len(block_end)}')
			
		if len(expression_start) != len(expression_end):
			raise RuntimeError(f'{self.expression_start} and {self.expression_end} tags count mismatch: {len(expression_start)} != {len(expression_end)}')
	
		# Sort
		ordered_tags  = one_time_block_start + one_time_block_end
		ordered_tags += one_time_expression_start + one_time_expression_end
		ordered_tags += block_start + block_end
		ordered_tags += expression_start + expression_end
		ordered_tags = sorted(ordered_tags, key=lambda x: x[0])
		
		# Validate order
		if len(ordered_tags):
			cursor = 0
			
			last_open_tag_id = -1
			while cursor < len(ordered_tags):
				if last_open_tag_id != -1:
					if ordered_tags[cursor][1] - 1 != last_open_tag_id:
						raise RuntimeError(f'Unmatched {tag_by_id[last_open_tag_id]} tag')
					# else
					last_open_tag_id = -1
				else:
					if ordered_tags[cursor][1] % 2 == 1:
						raise RuntimeError(f'Unmatched {tag_by_id[ordered_tags[cursor][1]]} tag')
					# else
					last_open_tag_id = ordered_tags[cursor][1]
				
				cursor += 1
			
			if last_open_tag_id != -1:
				if ordered_tags[cursor][1] - 1 != last_open_tag_id:
					raise RuntimeError(f'Unmatched {tag_by_id[last_open_tag_id]} tag')
		
		
		# ---> Third pass: split source into separate aprts depending on the type
		
		if len(ordered_tags) == 0:
			return [ StringTemplateFragment(source) ]
		
		template_fragments = []
		# Count acurrencies of each tag type
		fragment_types_count = [ 0 ] * 4
		
		last_source_index = 0
		for cursor in range(0, len(ordered_tags), 2):
			# Append missing string as text node
			if last_source_index < ordered_tags[cursor][0]:
				substring = source[last_source_index : ordered_tags[cursor][0]]
				if self.strip_string:
					substring = substring.strip()
				
				if len(substring):
					template_fragments.append(StringTemplateFragment(substring))
			
			substring = source[ordered_tags[cursor][0] + len(tag_by_id[ordered_tags[cursor][1]]) : ordered_tags[cursor + 1][0]]
			fragment_types_count[ordered_tags[cursor][1] // 2] += 1
			
			# Skip empty blocks
			if len(substring.strip()) == 0:
				last_source_index = ordered_tags[cursor + 1][0] + len(tag_by_id[ordered_tags[cursor + 1][1]])
				continue
			
			if ordered_tags[cursor][1] == 0:
				template_fragments.append(BlockTemplateFragment(substring, one_time=True, block_start_tag=self.one_time_block_start, block_end_tag=self.one_time_block_end, save_source=self.save_source_string, _tag_index=fragment_types_count[ordered_tags[cursor][1] // 2]))
			
			elif ordered_tags[cursor][1] == 2:
				template_fragments.append(ExpressionTemplateFragment(substring, one_time=True, expression_start_tag=self.one_time_expression_start, expression_end_tag=self.one_time_expression_end, save_source=self.save_source_string, _tag_index=fragment_types_count[ordered_tags[cursor][1] // 2]))
			
			elif ordered_tags[cursor][1] == 4:
				template_fragments.append(BlockTemplateFragment(substring, one_time=False, block_start_tag=self.one_time_block_start, block_end_tag=self.block_start, save_source=self.block_end, _tag_index=fragment_types_count[ordered_tags[cursor][1] // 2]))
			
			elif ordered_tags[cursor][1] == 6:
				template_fragments.append(ExpressionTemplateFragment(substring, one_time=False, expression_start_tag=self.expression_start, expression_end_tag=self.expression_end, save_source=self.save_source_string, _tag_index=fragment_types_count[ordered_tags[cursor][1] // 2]))
			
			last_source_index = ordered_tags[cursor + 1][0] + len(tag_by_id[ordered_tags[cursor + 1][1]])
			
		# Append the rest
		if last_source_index < len(source):
			substring = source[last_source_index : len(source)]
			if self.strip_string:
				substring = substring.strip()
			
			if len(substring):
				template_fragments.append(StringTemplateFragment(substring))
		
		return template_fragments


class Template:
	"""
	Represents single template instance that can be loaded from file or input 
	string. Supports iterator rendering,s tring and file rendering.
	
	Default configuration for parser is:
	```
	ONE_TIME_BLOCK_START is '{1{!'
	ONE_TIME_BLOCK_END is '!}1}'
	ONE_TIME_EXPRESSION_START is '{1{%'
	ONE_TIME_EXPRESSION_END is '%}1}'
	COMMENT_BLOCK_START is '{{#'
	COMMENT_BLOCK_END is '#}}'
	BLOCK_START is '{{!'
	BLOCK_END is '!}}'
	EXPRESSION_START is '{{%'
	EXPRESSION_END is '%}}'
	```
	
	By default identation may vary from 0 to infinity because parser 
	automatically removes all excessive ident from input fragment:
	```
	____def myfun():
	________return '13'
	____aboba = 'beb'
	```
	Turns into:
	```
	def myfun():
	____return '13'
	aboba = 'beb'
	```
	
	Syntax of one-time blocks and expressions:
	```
	{1{!
		global something
		something = 'this code will be executed once inside .init()'
		nothing = 'global keyword works as if this code block is inside function'
		anything = 'global variables are shared among all code blocks'
	!}1}
	```
	
	```
	{1{%
		f\"""
		<title>{something}</title>
		<content>This code is evaluated on .init() and result replaces the source code block</content>
		\"""
	%}1}
	```
	
	Syntax of render-time blocks and expressions:
	```
	{{!
		# Following function will return unique value per each .render() because it closures the value of timetamp variable
		timestamp = time.time()
		global myfunc
		def myfunc():
			return timestamp
	!}}
	```
	
	```
	{{%
		f\"""
		<span>timestamp not is: {myfunc()}</span>
		\"""
	%}}
	```
	
	Syntax of comment blocks:
	```
	{{#
		The following block is comment block and it's contents are removed from the resulting render
		
		{{%
			'this value is never used'
		%}}
	#}}
	```
	"""
	
	def __init__(self, source: str, template_parser: TemplateParser=None, context: dict=None):
		"""
		Initialize template from the given source and parse it.
		
		If given template contains one-time-init code blocks or segments, they 
		are evaluted with .init() call.
		
		`template_parser` defines default aprsed to use for this Template. In 
		case oof None, default configuration is used.
		
		`context` defines global context to use in this template. If it is not 
		set, new context is created for the template.
		"""
		
		template_parser = template_parser or TemplateParser()
		self.fragments = template_parser.parse(source) if source is not None else []
		self.context = context
		
		# Template should be initialized before use
		self.initialized = True
		for fragment in self.fragments:
			if fragment.is_one_time():
				self.initialized = False
				break
	
	def is_initialized(self) -> bool:
		"""
		Returns Triue if template was initialized. Template is initialized by 
		default if it does not contain any one-time init blocks.
		"""
		return self.initialized
	
	async def init(self, scope: dict=None, strip_string: bool=True, none_ok: bool=False, init_ok: bool=False, reuse_scope: bool=True) -> 'Template':
		"""
		Performs initialization of the Template and evaluates all one-time-init 
		blocks.
		
		Returns this template, so call to init() supports inline execution:
		```
		Template.from_file('template.thtml').init(init_ok=True).render()
		```
		
		`scope` defines the arguments dict with arguemtns that are uniquly passed 
		to each one-time block or expression wrapped into dict(), as locals.
		
		`strip_string` sets enable strip result of ExpressionTemplateFragment 
		evaluation.
		
		`none_ok` sets ignore mode for None result of the expression. If set to 
		True, None result is not used in future template rendering.
		
		`init_ok` sets ignore already initialized state of template and does 
		nothing if template is already initialized.
		
		`reuse_scope` sets scope reusage mode. If scope is reused, it is passed 
		directly as locals. Else it is passed wrapped into dict(scope) call.
		
		After calling .init(), string representation of template will change and 
		all one-time init fragments will be replaced with string fragments or 
		removed depending on type.
		"""
		
		if self.initialized:
			if init_ok:
				return self
			raise RuntimeError('Template already initialized')
		
		scope = scope or {}
		to_remove = []
		for i, fragment in enumerate(self.fragments):
			if fragment.is_one_time():
				if isinstance(fragment, BlockTemplateFragment):
					
					to_remove.append(i)
					await fragment.render(context=self.context, scope=(scope if reuse_scope else dict(scope)))
					
				elif isinstance(fragment, ExpressionTemplateFragment):
					
					value = await fragment.render(context=self.context, scope=(dict(scope) if scope else {}))
					if not none_ok and value is None:
						raise RuntimeError(f'Expression returned None at {fragment.evaluable.co_filename}')
					
					# Remove self if None
					if value is None:
						to_remove.append(i)
						continue
					
					# To string
					value = str(value)
					
					# Remove empty
					if strip_string:
						value = value.strip()
						if len(value) == 0:
							to_remove.append(i)
							continue
					
					# Insert string instead
					self.fragments[i] = StringTemplateFragment(value)
					
				else:
					raise RuntimeError(f'Unexpected type of one-time init fragment {type(fragment)}')
		
		to_remove = set(to_remove)
		self.fragments[:] = [ f for i, f in enumerate(self.fragments) if i not in to_remove ]
		self.initialized = True
		return self
	
	async def render_generator(self, scope: dict=None, strip_string: bool=True, none_ok: bool=False, reuse_scope: bool=True) -> typing.AsyncGenerator[str, None]:
		"""
		Render given template using generator over fragments. Returns string 
		representation of each fragment rendered.
		
		`scope` defines the arguments dict with arguemtns that are uniquly passed 
		to each one-time block or expression wrapped into dict(), as locals.
		
		`strip_string` sets enable strip result of ExpressionTemplateFragment 
		evaluation.
		
		`none_ok` sets ignore mode for None result of the expression. If set to 
		True, None result is not used in future template rendering.
		
		`reuse_scope` sets scope reusage mode. If scope is reused, it is passed 
		directly as locals. Else it is passed wrapped into dict(scope) call.
		
		Requires call to .init() if template was not initialized.
		"""
		
		if not self.initialized:
			raise RuntimeError('Template not initialized')
		
		scope = scope or {}
		for fragment in self.fragments:
			if isinstance(fragment, BlockTemplateFragment):
				
				await fragment.render(context=self.context, scope=(scope if reuse_scope else dict(scope)))
				
			else:
				
				value = await fragment.render(context=self.context, scope=(dict(scope) if scope else {}))
				if not none_ok and value is None:
					raise RuntimeError(f'Expression returned None at {fragment.evaluable.co_filename}')
				
				# Remove self if None
				if value is None:
					continue
				
				# To string
				value = str(value)
				
				# Remove empty
				if strip_string:
					value = value.strip()
					if len(value) == 0:
						continue
				
				# Insert string instead
				yield value
	
	async def render_string(self, scope: dict=None, strip_string: bool=True, none_ok: bool=False, reuse_scope: bool=True) -> str:
		"""
		Render given template into string from fragments. Returns string 
		representation of entire template rendered.
		
		`scope` defines the arguments dict with arguemtns that are uniquly passed 
		to each one-time block or expression wrapped into dict(), as locals.
		
		`strip_string` sets enable strip result of ExpressionTemplateFragment 
		evaluation.
		
		`none_ok` sets ignore mode for None result of the expression. If set to 
		True, None result is not used in future template rendering.
		
		`reuse_scope` sets scope reusage mode. If scope is reused, it is passed 
		directly as locals. Else it is passed wrapped into dict(scope) call.
		
		Requires call to .init() if template was not initialized.
		"""
		
		return ''.join([ f async for f in self.render_generator(scope, strip_string, none_ok, reuse_scope) ])
	
	async def render_file(self, filename: str, scope: dict=None, strip_string: bool=True, none_ok: bool=False, reuse_scope: bool=True) -> None:
		"""
		Render given template into file from fragments.
		
		`scope` defines the arguments dict with arguemtns that are uniquly passed 
		to each one-time block or expression wrapped into dict(), as locals.
		
		`strip_string` sets enable strip result of ExpressionTemplateFragment 
		evaluation.
		
		`none_ok` sets ignore mode for None result of the expression. If set to 
		True, None result is not used in future template rendering.
		
		`reuse_scope` sets scope reusage mode. If scope is reused, it is passed 
		directly as locals. Else it is passed wrapped into dict(scope) call.
		
		Requires call to .init() if template was not initialized.
		"""
		
		with open(filename, 'w', encoding='utf-8') as file:
			async for f in self.render_generator(scope, strip_string, none_ok, reuse_scope):
				file.write(f)
	
	def from_file(file: typing.Union[str, typing.TextIO], template_parser: TemplateParser=None, context: dict=None) -> 'Template':
		"""
		Load and parse template from given `file`. File can be either fileIO 
		wrapper or string file path.
		
		Example:
		```
		# Load from file object
		Template.from_file(open('myfile.thtml'))
		
		# Load from file name
		Template.from_file('myfile.thtml')
		```
		"""
		
		if isinstance(file, str):
			with open(file, 'r', encoding='utf-8') as file_obj:
				return Template(file_obj.read(), template_parser, context)
		
		return Template(file.read(), template_parser, context)
	
	def from_string(source: str, template_parser: TemplateParser=None, context: dict=None) -> 'Template':
		"""
		Load and parse template from given `source` string.
		"""
		
		return Template(source, template_parser, context)
	
	def from_fragments(fragments: typing.List[TemplateFragment], context: dict=None) -> 'Template':
		"""
		Construct Template from the given list of fragments. Returns new 
		Template from fragments and checks if it needs .init() call.
		"""
		
		template = Template(None, None, context)
		template.fragments = fragments
		
		template.initialized = True
		for fragment in template.fragments:
			if fragment.is_one_time():
				template.initialized = False
				break
		
		return template
	
	def __str__(self):
		return ('\n' if self.template_parser.strip_string else '').join([ str(f) for f in self.fragments ])
	
	def __repr__(self):
		return ('\n' if self.template_parser.strip_string else '').join([ str(f) for f in self.fragments ])


class FileWatcherTemplate:
	"""
	Class that defines cached Template wrapper based on filesystem template 
	watching. Template is loaded from silesystem and revalidated each time when 
	source template file is updated.
	
	Interfaces all render methods from base template class and supports 
	additional up_to_date flag.
	"""
	
	def __init__(
			self, 
			filename: str, 
			template_parser: TemplateParser=None, 
			context: dict=None, 
			init_scope: dict=None, 
			init_strip_string: bool=True,
			init_none_ok: bool=False,
			init_reuse_scope: bool=True
		):
		"""
		Create shadow tempalte without loading. Loading is performed with 
		manual call to `update()` or on `.render()` call.
		
		`init_` parameters are used to define arguments for late `.init()` call.
		"""
		
		self.filename        = filename
		self.timestamp       = None
		self.template        = None
		# Lock required to update template from disk
		self.template_lock   = asyncio.Lock()
		self.template_parser = template_parser or TemplateParser()
		self.context         = context
		self.init_scope        = init_scope
		self.init_strip_string = init_strip_string
		self.init_none_ok      = init_none_ok
		self.init_reuse_scope  = init_reuse_scope
	
	def is_up_to_date(self):
		"""
		Returns True if Template is up to date. Template us up to date if it was 
		loaded and it's file still exists and have modification date less than 
		it was when tempalte has been loaded.
		"""
		
		return not (self.timestamp is None or not os.path.exists(self.filename) or os.path.getmtime(self.filename) > self.timestamp)
	
	async def update(self):
		"""
		Performs updating of the tempalte from file. if `is_up_to_date()` returs 
		True, does nothing.
		
		If failure occurs, raises error depending on the situation.
		Uses async lock to perfom syncronization between calls to prevent race 
		condition and multiple parsings per tempalte.
		"""
		
		if self.is_up_to_date():
			return
		
		async with self.template_lock:
			
			# Fallback
			if self.is_up_to_date():
				return
			
			# Prevent keep in memory
			self.template  = None
			self.timestamp = None
			
			# Load
			self.template = Template.from_file(self.filename, self.template_parser, self.context)
			self.template.init(
				scope=self.init_scope, 
				strip_string=self.init_strip_string, 
				none_ok=self.init_none_ok, 
				init_ok=True, 
				reuse_scope=self.init_reuse_scope
			)
			self.timestamp = os.path.getmtime(self.filename)
	
	async def render_generator(self, scope: dict=None, strip_string: bool=True, none_ok: bool=False, reuse_scope: bool=True, auto_reload: bool=True) -> typing.AsyncGenerator[str, None]:
		"""
		Render given template using generator over fragments. Returns string 
		representation of each fragment rendered.
		
		`scope` defines the arguments dict with arguemtns that are uniquly passed 
		to each one-time block or expression wrapped into dict(), as locals.
		
		`strip_string` sets enable strip result of ExpressionTemplateFragment 
		evaluation.
		
		`none_ok` sets ignore mode for None result of the expression. If set to 
		True, None result is not used in future template rendering.
		
		`reuse_scope` sets scope reusage mode. If scope is reused, it is passed 
		directly as locals. Else it is passed wrapped into dict(scope) call.
		
		Automatically reloads template on file change if `auto_reload=True`.
		"""
		
		if auto_reload:
			await self.update()
		
		return await self.template.render_generator(scope=scope, strip_string=strip_string, none_ok=none_ok, reuse_scope=reuse_scope)
	
	async def render_string(self, scope: dict=None, strip_string: bool=True, none_ok: bool=False, reuse_scope: bool=True, auto_reload: bool=True) -> str:
		"""
		Render given template into string from fragments. Returns string 
		representation of entire template rendered.
		
		`scope` defines the arguments dict with arguemtns that are uniquly passed 
		to each one-time block or expression wrapped into dict(), as locals.
		
		`strip_string` sets enable strip result of ExpressionTemplateFragment 
		evaluation.
		
		`none_ok` sets ignore mode for None result of the expression. If set to 
		True, None result is not used in future template rendering.
		
		`reuse_scope` sets scope reusage mode. If scope is reused, it is passed 
		directly as locals. Else it is passed wrapped into dict(scope) call.
		
		Automatically reloads template on file change if `auto_reload=True`.
		"""
		
		if auto_reload:
			await self.update()
		
		return await self.template.render_string(scope=scope, strip_string=strip_string, none_ok=none_ok, reuse_scope=reuse_scope)
	
	async def render_file(self, filename: str, scope: dict=None, strip_string: bool=True, none_ok: bool=False, reuse_scope: bool=True, auto_reload: bool=True) -> str:
		"""
		Render given template into file from fragments.
		
		`scope` defines the arguments dict with arguemtns that are uniquly passed 
		to each one-time block or expression wrapped into dict(), as locals.
		
		`strip_string` sets enable strip result of ExpressionTemplateFragment 
		evaluation.
		
		`none_ok` sets ignore mode for None result of the expression. If set to 
		True, None result is not used in future template rendering.
		
		`reuse_scope` sets scope reusage mode. If scope is reused, it is passed 
		directly as locals. Else it is passed wrapped into dict(scope) call.
		
		Requires call to .init() if template was not initialized.
		"""
		
		if auto_reload:
			await self.update()
		
		return await self.template.render_file(filename=filename, scope=scope, strip_string=strip_string, none_ok=none_ok, reuse_scope=reuse_scope)

	def __str__(self):
		if self.timestamp is None:
			return None
		
		return self.template.__str__()
	
	def __repr__(self):
		if self.timestamp is None:
			return None
		
		return self.template.__repr__()











