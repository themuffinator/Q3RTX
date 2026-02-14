project(
  'q3rtx',
  'c',
  version: '0.1.0',
  meson_version: '>=1.3.0',
  default_options: [
    'c_std=gnu11,c11',
    'b_vscrt=static_from_buildtype',
    'warning_level=2',
  ],
)

host_system = host_machine.system()
is_windows = host_system == 'windows'
is_linux = host_system == 'linux'
is_darwin = host_system == 'darwin'

if not (is_windows or is_linux or is_darwin)
  error('Supported Meson host systems are windows, linux, and darwin.')
endif

cc = meson.get_compiler('c')
python = import('python').find_installation('python3', required: true)
fs = import('fs')
if is_windows
  windows_mod = import('windows')
endif

engine_name = 'q3rtx'
renderer_prefix = engine_name
renderer_name = 'rtx'

build_cfg = 'Release'
if get_option('buildtype').startswith('debug')
  build_cfg = 'Debug'
endif

source_root = meson.project_source_root()
vcxproj_dir = source_root / 'code' / 'win32' / 'msvc2017'
vcxproj_parser = source_root / 'scripts' / 'vcxproj_sources.py'
cpu_family = host_machine.cpu_family()

renderer_arch = cpu_family
if cpu_family == 'x86'
  if is_windows or is_linux
    renderer_arch = 'x86'
  else
    renderer_arch = 'i386'
  endif
elif cpu_family == 'aarch64'
  if is_windows
    renderer_arch = 'arm64'
  else
    renderer_arch = 'aarch64'
  endif
endif

renderer_module_name = renderer_prefix + '_' + renderer_name + '_' + renderer_arch

if not fs.exists(source_root / 'code' / 'rendererrtx')
  error('Missing code/rendererrtx. Copy code/renderervk to code/rendererrtx first.')
endif

# Use x64 project entries as canonical source map, then apply host-specific filtering.
platform_cfg = 'x64'

quake3e_src_text = run_command(
  python,
  vcxproj_parser,
  vcxproj_dir / 'quake3e.vcxproj',
  '--config',
  build_cfg,
  '--platform',
  platform_cfg,
  '--root',
  source_root,
  '--exclude',
  'code/win32/win_qgl.c',
  check: true,
).stdout().strip()

renderervk_src_text = run_command(
  python,
  vcxproj_parser,
  vcxproj_dir / 'renderervk.vcxproj',
  '--config',
  build_cfg,
  '--platform',
  platform_cfg,
  '--root',
  source_root,
  check: true,
).stdout().strip()

botlib_src_text = run_command(
  python,
  vcxproj_parser,
  vcxproj_dir / 'botlib.vcxproj',
  '--config',
  build_cfg,
  '--platform',
  platform_cfg,
  '--root',
  source_root,
  check: true,
).stdout().strip()

libjpeg_src_text = run_command(
  python,
  vcxproj_parser,
  vcxproj_dir / 'libjpeg.vcxproj',
  '--config',
  build_cfg,
  '--platform',
  platform_cfg,
  '--root',
  source_root,
  check: true,
).stdout().strip()

libogg_src_text = run_command(
  python,
  vcxproj_parser,
  vcxproj_dir / 'libogg.vcxproj',
  '--config',
  build_cfg,
  '--platform',
  platform_cfg,
  '--root',
  source_root,
  check: true,
).stdout().strip()

libvorbis_src_text = run_command(
  python,
  vcxproj_parser,
  vcxproj_dir / 'libvorbis.vcxproj',
  '--config',
  build_cfg,
  '--platform',
  platform_cfg,
  '--root',
  source_root,
  check: true,
).stdout().strip()

if quake3e_src_text == '' or renderervk_src_text == ''
  error('Failed to resolve required source files from vcxproj.')
endif

quake3e_paths = quake3e_src_text.split('\n')
common_client_paths = []
win_client_paths = []

foreach src : quake3e_paths
  if src.startswith('code/win32/')
    if src != 'code/win32/win_qgl.c'
      win_client_paths += src
    endif
  else
    common_client_paths += src
  endif
endforeach

if cpu_family == 'aarch64'
  arm64_client_paths = []
  foreach src : common_client_paths
    if src != 'code/qcommon/vm_x86.c'
      arm64_client_paths += src
    endif
  endforeach
  common_client_paths = arm64_client_paths
  common_client_paths += 'code/qcommon/vm_aarch64.c'
elif cpu_family == 'arm'
  arm_client_paths = []
  foreach src : common_client_paths
    if src != 'code/qcommon/vm_x86.c'
      arm_client_paths += src
    endif
  endforeach
  common_client_paths = arm_client_paths
  common_client_paths += 'code/qcommon/vm_armv7l.c'
endif

if not is_windows
  if cpu_family == 'x86_64'
    common_client_paths += 'code/asm/snd_mix_x86_64.s'
  elif cpu_family == 'x86'
    common_client_paths += [
      'code/asm/snd_mix_mmx.s',
      'code/asm/snd_mix_sse.s',
    ]
  endif
endif

unix_sdl_paths = [
  'code/unix/unix_main.c',
  'code/unix/unix_shared.c',
  'code/unix/linux_signals.c',
  'code/sdl/sdl_glimp.c',
  'code/sdl/sdl_gamma.c',
  'code/sdl/sdl_input.c',
  'code/sdl/sdl_snd.c',
]

platform_client_paths = is_windows ? win_client_paths : unix_sdl_paths

rendererrtx_paths = []
foreach src : renderervk_src_text.split('\n')
  rendererrtx_paths += src.replace('code/renderervk/', 'code/rendererrtx/')
endforeach

quake3e_sources = files(common_client_paths + platform_client_paths)
rendererrtx_sources = files(rendererrtx_paths)
renderer_aux_sources = files(
  'code/qcommon/q_shared.c',
  'code/qcommon/puff.c',
  'code/qcommon/q_math.c',
)
botlib_sources = files(botlib_src_text.split('\n'))
libjpeg_sources = files(libjpeg_src_text.split('\n'))
libogg_sources = files(libogg_src_text.split('\n'))
libvorbis_sources = files(libvorbis_src_text.split('\n'))

include_paths = [
  'code',
  'code/botlib',
  'code/client',
  'code/qcommon',
  'code/renderercommon',
  'code/rendererrtx',
  'code/server',
  'code/libjpeg',
  'code/libogg/include',
  'code/libvorbis/include',
]

if is_windows
  include_paths += [
    'code/win32',
    'code/libcurl/windows/include',
  ]
else
  include_paths += [
    'code/unix',
    'code/sdl',
  ]
endif

common_includes = include_directories(include_paths)

renderer_c_args = []
if is_windows
  renderer_c_args += '-D_CRT_SECURE_NO_WARNINGS'
endif
renderer_c_args += [
  '-DUSE_RENDERER_DLOPEN',
  '-DUSE_VULKAN_API',
]

renderer = shared_library(
  renderer_module_name,
  rendererrtx_sources + renderer_aux_sources,
  include_directories: common_includes,
  c_args: renderer_c_args,
  name_prefix: '',
  install: false,
)

botlib = static_library(
  'botlib',
  botlib_sources,
  include_directories: common_includes,
  c_args: [
    '-DBOTLIB',
    '-D_CRT_SECURE_NO_DEPRECATE',
  ],
)

libjpeg = static_library(
  'libjpeg_local',
  libjpeg_sources,
  include_directories: common_includes,
  override_options: [
    'warning_level=1',
  ],
  c_args: [
    '-D_CRT_SECURE_NO_DEPRECATE',
  ],
)

libogg = static_library(
  'libogg_local',
  libogg_sources,
  include_directories: common_includes,
  override_options: [
    'warning_level=1',
  ],
)

libvorbis = static_library(
  'libvorbis_local',
  libvorbis_sources,
  include_directories: common_includes,
  override_options: [
    'warning_level=0',
  ],
  c_args: [
    '-D_CRT_SECURE_NO_WARNINGS',
  ],
  link_with: [
    libogg,
  ],
)

engine_deps = []

if is_windows
  engine_deps += [
    cc.find_library('advapi32', required: true),
    cc.find_library('comctl32', required: true),
    cc.find_library('crypt32', required: true),
    cc.find_library('gdi32', required: true),
    cc.find_library('ole32', required: true),
    cc.find_library('winmm', required: true),
    cc.find_library('wldap32', required: true),
    cc.find_library('wsock32', required: true),
    cc.find_library('ws2_32', required: true),
  ]
else
  engine_deps += dependency('sdl2', required: true)
  libm = cc.find_library('m', required: false)
  if libm.found()
    engine_deps += libm
  endif
  libdl = cc.find_library('dl', required: false)
  if libdl.found()
    engine_deps += libdl
  endif
endif

if get_option('with_curl')
  if is_windows
    curl_dir = source_root / 'code' / 'libcurl' / 'windows' / 'vs2017' / 'lib64'
    curl_name = build_cfg == 'Debug' ? 'curl_a_debug' : 'curl_a'
    engine_deps += cc.find_library(curl_name, dirs: [curl_dir], required: true)
  else
    engine_deps += dependency('libcurl', required: true)
  endif
endif

q3rtx_c_args = [
  '-DUSE_RENDERER_DLOPEN',
  '-DRENDERER_PREFIX="q3rtx"',
  '-DRENDERER_DEFAULT=rtx',
  '-DUSE_OGG_VORBIS',
  '-DUSE_SKIPIDLOGO',
  '-DUSE_VULKAN_API',
]

if is_windows
  q3rtx_c_args += [
    '/Zc:preprocessor-',
    '-DWIN32',
    '-D_WIN32',
    '-D_WINDOWS',
    '-D_CRT_SECURE_NO_DEPRECATE',
    '-D_WINSOCK_DEPRECATED_NO_WARNINGS',
  ]
elif is_darwin
  q3rtx_c_args += '-DMACOS_X'
endif

if get_option('with_curl')
  q3rtx_c_args += '-DUSE_CURL'
  if is_windows
    q3rtx_c_args += '-DCURL_STATICLIB'
  endif
endif

if is_windows
  if cpu_family == 'x86_64'
    q3rtx_name = engine_name + '.x64'
  elif cpu_family == 'aarch64'
    q3rtx_name = engine_name + '.arm64'
  else
    q3rtx_name = engine_name
  endif
else
  q3rtx_name = engine_name
endif

q3rtx_all_sources = quake3e_sources
if is_windows
  q3rtx_all_sources += windows_mod.compile_resources('code/win32/win_resource.rc')
endif

if is_windows
  executable(
    q3rtx_name,
    q3rtx_all_sources,
    include_directories: common_includes,
    c_args: q3rtx_c_args,
    link_with: [
      botlib,
      libjpeg,
      libogg,
      libvorbis,
    ],
    dependencies: engine_deps,
    win_subsystem: 'windows',
    install: false,
  )
else
  executable(
    q3rtx_name,
    q3rtx_all_sources,
    include_directories: common_includes,
    c_args: q3rtx_c_args,
    link_with: [
      botlib,
      libjpeg,
      libogg,
      libvorbis,
    ],
    dependencies: engine_deps,
    install: false,
  )
endif

if not fs.exists(source_root / 'baseq3')
  message('baseq3 was not found in repository root. Runtime requires external game data.')
endif
