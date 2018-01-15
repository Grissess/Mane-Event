Don't run m4 directly on this file; instead, use the `include' macro.

Joins all non-empty arguments from the second on using the first as a separator
between.
define(`join', `ifelse(`$#', `2', ``$2'', `ifelse(`$2', `', `', ``$2'_')$0($1, shift(shift($@)))')')
define(`_join', `ifelse(`$#$2', `2', `', `ifelse(`$2', `', `', ``$1$2'')$0($1, shift(shift($@)))')')

Apply the unadic macro named by the first argument to each argument, providing
a comma-separated list suitable for consumption by another reducing macro (like
join).
define(`map', `ifelse(eval(`$# < 2'), `1', `', `ifelse(`$#$2', `2', `', `ifelse(`$2', `', `', `$1(`$2')'),$0(`$1', shift(shift($@)))')')')

Split the given argument into characters, separated by commas, suitable for
consumption by another reducing macro (like join).
define(`chars', `ifelse(len(`$1'), `0', `', len(`$1'), `1', `$1', `substr(`$1', `0', `1'),$0(substr(`$1', `1'))')')

RE-generating macros
define(`seq', ``'(?:join(`', $@))')
define(`alt', ``'(?:join(`|', $@))')
define(`rep', ``'(?:(?:$1)ifelse(`$2$3', `', `*', `$2,$3', `1,', `+', `$2,$3', `,1', `?', `{$2,$3}'))')
define(`opt', `rep(`$1', `', `1')')
define(`zmore', `rep(`$1', `', `')')
define(`omore', `rep(`$1', `1', `')') 
define(`ucs', `\U`'eval(`0x'$1, `16', `8')')
define(`capt', ``'($1)')

Higher level RE macros
define(`word_sep', `zmore(`[^a-zA-Z0-9]')')
define(`seq_sep', ``'(?:join(word_sep, $@))')
define(`rep_sep', ``'(?:(?:$1`'word_sep)ifelse(`$2$3', `', `*', `$2,$3', `1,', `+', `$2,$3', `,1', `?', `{$2,$3}'))')
define(`zmore_sep', `rep_sep(`$1', `', `')')
define(`omore_sep', `rep_sep(`$1', `1', `')')
define(`ws_begin', `alt(`^', `\s+')')
define(`ws_end', `alt(`$', `\s+')')

Phonetic classes
define(`ph_f', `alt(omore_sep(`f'), seq_sep(`p', omore_sep(`h')))')
define(`ph_k', `omore_sep(alt(`c', `k', `q'))')
define(`ph_x', `alt(omore_sep(`x'), seq_sep(opt(ph_k), `s'))')
define(`ph_ch', `alt(seq_sep(opt(`t'), omore_sep(`c'), omore_sep(`h')), rep_sep(`c', `2', `'))')
The following two include relevant emoji:
define(`ph_b', `alt(`b', ucs(`1F171'))')
define(`ph_p', `alt(`p', ucs(`1F17F'))')
define(`ph_ss', `rep_sep(alt(`s', `z'), `2', `')')
Numeric substitutions:
define(`ns_o', `alt(`o', `0')')
define(`ns_e', `alt(`e', `3')')
define(`ns_l', `alt(`l', `1')')
define(`ns_i', `alt(`i', `1', `l')')
define(`ns_a', `alt(`a', `4')')
