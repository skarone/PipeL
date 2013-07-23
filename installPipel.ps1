$save_dir=Resolve-Path ~/Downloads

function InstallPythonMSI($installer, $target) {
	$Arguments = @()
	$Arguments += "/i"
	$Arguments += "`"$installer`""
	$Arguments += "TARGETDIR=`"$target`""
	$Arguments += "ALLUSERS=`"1`""
	$Arguments += "/passive"

	Start-Process "msiexec.exe" -ArgumentList $Arguments -Wait
}

function InstallPyQtMSI($installer) {
	$Arguments = @()
	$Arguments += "/i"
	$Arguments += "`"$installer`""
	$Arguments += "ALLUSERS=`"1`""
	$Arguments += "/passive"

	#Start-Process $installer -ArgumentList $Arguments -Wait
	Start-Process $installer
}

function get-python-ver($version) {
	$clnt = new-object System.Net.WebClient;
	$filename = 'python-' + $version + '.amd64.msi';
	# use ('' + $save_dir) to make it a string
	$save_path = '' + $save_dir + '\' + $filename;
	$save_path;
	if(!(Test-Path -pathType container $save_dir)) {
		# print something
		exit;
	}
	#if(!(Test-Path -pathType leaf $save_path)) {
	$result = Test-Path $save_path;
	$result;
	if(!( $result ) ) {
		# get the file
		$url = 'http://www.python.org/ftp/python/' + $version + '/' + $filename;
		$url;
		$clnt.DownloadFile($url, $save_path);
	}
	$short_ver = $version.replace('.', '').substring(0,2);
	$target_dir = $env:programfiles + '\Python' + $short_ver;
	$target_spec = "TARGETDIR=`"$target_dir`""
	InstallPythonMSI $save_path $target_dir
	if($version -like '2*') {
		$urllib_cmd = 'import urllib2, sys; eval(compile(urllib2.';
	} else {
		$urllib_cmd = 'import urllib.request, sys; eval(compile(urllib.request.';
	}
	$urllib_cmd += "urlopen('http://python-distribute.org/distribute_setup.py').read(), 'distribute_setup', 'exec'))";
	& ($target_dir + '\python.exe') -c $urllib_cmd
	del distribute-*.tar.gz

	# lib2to3 has an issue where it tries to write files to the lib directory,
	#  which causes easy_install to fail with a Sandbox Violation. Bypass
	#  this error by pre-loading the grammar.
	& ($target_dir + '\Python.exe') -c "import lib2to3.pygram"
}

function bootstrap-python() {
	cmd /c mklink /d C:\Python "C:\Program Files\Python27"
	\python\scripts\easy_install jaraco.windows
	\python\scripts\enver 'path=c:\python;c:\python\scripts'
	\python\scripts\enver 'pathext=.py;.pyw'
	\python\scripts\enver 'VIRTUALENV_DISTRIBUTE=True'
	# update file associations to point to \Python
	$MyInvocation = (Get-Variable MyInvocation -Scope 1).Value
	$scriptpath = $MyInvocation.MyCommand.Path
	$this_dir = Split-Path $scriptpath
	\python\python.exe ($this_dir+"\install\associations.py")
}

function install-pymodules(){
	cmd /c mklink /d C:\Python "C:\Program Files\Python27"
	\python\scripts\easy_install poster
	\python\scripts\easy_install httplib2
	\python\scripts\easy_install mechanize
}

function installPyQt(){
	cmd /c mklink /d C:\Python "C:\Program Files\Python27"
	$filename = 'PyQt4-4.10.2-gpl-Py2.7-Qt4.8.4-x64.exe';
	$MyInvocation = (Get-Variable MyInvocation -Scope 1).Value
	$scriptpath = $MyInvocation.MyCommand.Path
	$this_dir = Split-Path $scriptpath
	$save_path = '' + $this_dir + '\install\libs\' + $filename;
	$save_path
	InstallPyQtMSI $save_path
	\python\python.exe ($this_dir+"\install\installPyqtMaya.py")
}

get-python-ver 2.7.3
# get-python-ver 3.2.3
bootstrap-python
install-pymodules
installPyQt


