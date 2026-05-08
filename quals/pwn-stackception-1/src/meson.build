project('stackception', 'c',
  version: '0.1.0',
  default_options: [
    'warning_level=3',
    'werror=true',
    'c_std=c2x',
    'b_ndebug=if-release',
    'b_pie=true',
  ]
)

cc = meson.get_compiler('c')

cc_flags = [
  '-fstack-protector-strong',
  '-fno-omit-frame-pointer',
]
ld_flags = []

if cc.get_id() != 'clang'
  error('This project requires clang compiler')
endif

stackception_src = files('stackception.c')
stackception_asm_src = files('stackception-asm.c')
stackception_disasm_src = files('stackception-disasm.c')

executable('stackception-1',
  stackception_src,
  c_args: cc_flags + ['-DLEVEL=1'],
  install: true
)

executable('stackception-2',
  stackception_src,
  c_args: cc_flags + ['-DLEVEL=2'],
  install: true
)

executable('stackception-3',
  stackception_src,
  c_args: cc_flags + ['-DLEVEL=3', '-fsanitize=safe-stack'],
  link_args: ['-fsanitize=safe-stack'],
  install: true
)

executable('stackception-asm',
  stackception_asm_src,
  c_args: cc_flags,
  link_args: ld_flags,
  install: true
)

executable('stackception-disasm',
  stackception_disasm_src,
  c_args: cc_flags,
  link_args: ld_flags,
  install: true
)
