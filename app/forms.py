from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField, FloatField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, NumberRange, EqualTo

# class VMTemplateForm(FlaskForm):
#     template_name = StringField('Template Name', validators=[DataRequired()])
#     cpu_cores = IntegerField('CPU Cores', validators=[DataRequired(), NumberRange(min=1)])
#     memory = IntegerField('Memory (MB)', validators=[DataRequired(), NumberRange(min=512)])
#     disk_size = IntegerField('Disk Size (GB)', validators=[DataRequired(), NumberRange(min=1)])
#     network_adapter = SelectField('Network Adapter', choices=[
#         ('e1000', 'E1000'),
#         ('virtio', 'VirtIO'),
#         ('rtl8139', 'RTL8139')
#     ], validators=[DataRequired()])
#     os_type = SelectField('OS Type', choices=[
#         ('ubuntu', 'Ubuntu'),
#         ('centos', 'CentOS'),
#         ('debian', 'Debian'),
#         ('windows', 'Windows Server')
#     ], validators=[DataRequired()])
#     submit = SubmitField('Generate Template')

class CloudInitInstanceForm(FlaskForm):
    template = SelectField('VM Template')
    hostname = StringField('Hostname')
    username = StringField('Username')
    password = PasswordField('Password')
    ssh_key = TextAreaField('SSH Public Key')
    ip_address = StringField('IP Address')
    submit = SubmitField('Create Instance')

class TemplateForm(FlaskForm):
    template_id = SelectField('Pick Template', validators=[DataRequired()], choices=[])
    vm_node = SelectField('Pick Node', validators=[DataRequired()], choices=[])
    vm_name = StringField('VM Name', validators=[DataRequired()])
    vm_id = IntegerField('VM ID', validators=[DataRequired()])
    submit = SubmitField('Create VM')

class CloudInitInstanceForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    ssh_key = TextAreaField('SSH Key', validators=[DataRequired()])
    ip_address = StringField('IP Address', validators=[DataRequired()])
    submit = SubmitField('Create VM')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class ProxmoxConfigForm(FlaskForm):
    host = StringField('Proxmox Host', validators=[DataRequired()])
    user = StringField('Proxmox User', validators=[DataRequired()])
    password = PasswordField('Proxmox Password', validators=[DataRequired()])
    login_method = SelectField('Login Method', choices=["pam", "pve"], validators=[DataRequired()])
    submit = SubmitField('Save Configuration')