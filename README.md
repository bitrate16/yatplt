# YATplT
YATplT - Yet Another Template Thing

_notAdvanced template rendering thing_

# TL;DR

Template rendering
```python
template_string = """
{{# Create page with static rendered title and dynamic content #}}
{1{!
	# One time block
	import random
	
	titles = [
		'foo',
		'bar',
		'baz'
	]
	
	global page_title
	page_title = random.choice(titles)
!}1}

{{# Set title #}}
<title>{1{%
	# One time expression
	page_title
%}1}</title>

{{# Peek heavy data #}}
{{!
	# Render time block
	import time
	
	global lots_of_userdata
	lots_of_userdata = []
	
	# Simulate heavy work
	for i in range(100):
		lots_of_userdata.append(i)
		time.sleep(0.1)
!}}

{{# Fill with content #}}
{{!
	# Render time expression
	'<br>'.join([ f'<h1>{user}</h1>' for user in lots_of_userdata ])
!}}
"""

# Load
template = Template.from_string(source=template_string, context={})

# Init
await template.init(init_ok=True, strip_string=True, none_ok=True)

# Render
result = tempalte.render_string(args={}, strip_string=True, none_ok=True)

# Do anything
print(result)
```

# Basics
This template rendering thing is based on pure python expressions and code inside files. This allows using multiple different block types inside each file: comment blocks, statement blocks, expression blocks and one-time blocks. Statement blocks never return value, while expression blocks always return value and support None check.

Additional feature is automatic identation that helps used to write code more simple and formatted and do not cate about excessive identation.

With autoident, this code:
```python
		def myfun():
			return 42
		
		a = 37
```
Is turned into:
```python
def myfun():
	return 42

a = 37
```

### Comment blocks

Default comment block tags are: `{{#` and `#}}`. All code and text placed inside comment blocks is ignored and removed:

```python
{{#
	exit(0)
#}}
```

This type of blocks is the same as regular comments in your code `/* comment */`.

### One-time blocks and expressions

This type of blocks is a special one that allows user to execute some code when Template is initialized. by default Template is uninitialized if it has at least one code block that is one-time callable.

Following code defines global function that can be used in any code block later. This block is a statement without return value:
```python
{1{!
	global myfun
	def myfun(x):
		return x + 37
!}1}
```

Following code defines one-time expression that is evaluated during `.init()` call. After evaluation, result of this expression is inserted instead of this code block
```html
<h1>
{1{%
	myfun(42)
%}1}
</h1>
```
Will result in:
```html
<h1>
79
</h1>
```

### Render-time blocks and expressions

This type of blocks and expressions is different from one-time init blocks because these blocks are evaluated each time on `.render()` call.

This type of blocks also supports statement blocks that can define global variables too:
```python
{{!
	global gettimestamp
	
	# Enclosure local variable
	import time
	timestamp = time.time()
	
	def gettimestamp(x):
		return timestamps
!}}
```

Later this code can be used to evaluate expression blocks:
```html
<h1>
{{%
	myfun(gettimestamp())
%}}
</h1>
```
Will result in whatever your time is + 37:
```html
<h1>
1291238534263
</h1>
```

Despite to one-time blocks, these blocks are rendered on each call to `.render()`.

# Rendering

After dealing with basic block types, let's render something

### Template from different sources

This library supports different source of tempalte input ~~and all of them are slow~~.

#### File input:
```python
# By file name
template = yatplt.Template.from_file('myfile.thtml')

# By file object
template = yatplt.Template.from_file(open('myfile.thtml', 'r'))
```

#### String input:
```python
# From file myfile.thtml
template_string = """
<title>{{% username %}}</title>
<h1>{{% action %}}</h1>
"""

# Direct constructor
template = yatplt.Template(template_string)

# Indirect
template = yatplt.Template.from_string(template_string)
```

#### TemplateFragment list:
```python
# Same as above
# ExpressionTemplateFragment accepts python source code as input
fragments = [
	yatplt.StringTemplateFragment('<title>'),
	yatplt.ExpressionTemplateFragment('username'),
	yatplt.StringTemplateFragment('</title>\n<h1>')
	yatplt.ExpressionTemplateFragment('action'),
	yatplt.StringTemplateFragment('</h1>')
]

# Indirect
template = yatplt.Template.from_fragments(fragments)
```

### Advanced options for template construction

Template can be constructed with additional options that define future behavior of the template.

From example above
```python
# From file myfile.thtml
template_string = """
<title>{{% username %}}</title>
<h1>{{% action %}}</h1>
<<<
	this will disappear
>>>
"""

# Define global variables for this template
context = {
	'username': 'anonymous',
	'action': 'nothing'
}

# Custom parser where comment block is defined with <<< and >>>
template_parser = TemplateParser(comment_block_start='<<<', comment_block_end='>>>')

# Indirect
template = yatplt.Template.from_string(template_string, template_parser=template_parser, context=context)
```

### Rendering

Rendering operation supports different variants of render. Basic rendering enforces support for async expressions in python code snippets and each `.render()` call requires await.

Before render, initialize your template:
```python
# This dict defines variables that will be copied as locals() for this .init() call
args = {
	'key': 'value'
}

# Set init_ok to True to ignore already initialized error
# Set none_ok to True to ignore None value error in expressions
# Set strip_string to True to strip output of the expression fragments
template.init(args=args, init_ok=True, none_ok=True, strip_string=True)
```

#### Simple rendering using generator rendering:
```python
args = {
	'username': 'Pegasko',
	'action': 'Merp'
}

async for fragment in template.render_generator(args=args, init_ok=True, none_ok=True, strip_string=True):
	print(fragment)
```

#### Simple rendering to string:
```python
args = {
	'username': 'bitrate16',
	'action': '"DROP TABLE *;--'
}

print(await template.render_string(args=args, init_ok=True, none_ok=True, strip_string=True))
```

#### Simple rendering to file:
```python
args = {
	'username': 'odmin',
	'action': 'hak for mani'
}

print(await template.render_file('output.html', args=args, init_ok=True, none_ok=True, strip_string=True))
```

# Footer

~~Oh no, my PyHP colletion!~~

```
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
```
```
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
```