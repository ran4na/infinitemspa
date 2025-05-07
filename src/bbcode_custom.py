import bbcode

parser = bbcode.Parser(replace_links=False)

# Non-collapsing pesterlog tag.
def render_pesterlog(tag_name, value, options, parent, context):
    return f'<div class="pesterlog">{value}</div>'

#placeholder
def render_size(tag_name, value, options, parent, context):
    return f'<span class="size">{value}</span>'

#placeholder
def render_image(tag_name, value, options, parent, context):
    return f'<img src="{value}" style="max-width: 540px"/>'


parser.add_formatter('pesterlog', render_pesterlog)
parser.add_formatter('size', render_size)
parser.add_formatter('img', render_image)