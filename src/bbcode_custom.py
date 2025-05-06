import bbcode

parser = bbcode.Parser()

# Non-collapsing pesterlog tag.
def render_pesterlog(tag_name, value, options, parent, context):
    return f'<div class="pesterlog">{value}</div>'

#placeholder
def render_size(tag_name, value, options, parent, context):
    return f'<span class="size">{value}</span>'

parser.add_formatter('pesterlog', render_pesterlog)
parser.add_formatter('size', render_size)