divert(-1)
This file is an input to m4, a macro processor. The output is a file containing
a single-line RE that can be compiled and used as an obscenity filter. The
remaining part of this section is dedicated to defining the macros used to
generate the expression. On a device with m4 installed, simply run:

	$ m4 vulgar_re.m4 > vulgar.re

...to regenerate the file.

This file was tested against GNU m4, a very featureful and flexible m4;
however, the intended target is any POSIX-compliant m4. Please let the
maintainers of this repository know if you find a bug in another (conforming)
m4 implementation.

include(`re_util.m4')

Below the following diversion, please be careful to ensure that this file
generates only two lines--the first an admonition to check this file. By
necessity, there will be obscenity in here.
divert`'dnl
!!! THIS FILE IS AUTOMATICALLY GENERATED !!! Modify vulgar_re.m4 and regenerate. See that file for more details.
translit(`(?i)alt(map(`capt',
	ifelse(`Fuck and analogues:'),
	seq(seq_sep(ph_f, alt(omore_sep(`u'), ns_o, omore_sep(`a')), ph_k, opt(alt(seq_sep(alt(zmore_sep(ns_e), zmore_sep(ns_a)), omore_sep(`r')),seq_sep(opt(alt(ns_i, ns_e)), omore_sep(`n'), zmore_sep(`g'))))), ws_end),  dnl fuck[er|ing], fack, fuk etc.
	seq(seq_sep(ph_f, omore_sep(ns_a), omore_sep(`r'), alt(ph_k, omore_sep(`g'))), ws_end),  dnl farg, fark
	seq(seq_sep(ph_f, omore_sep(`r'), alt(omore_sep(ns_i), omore_sep(`a')), alt(ph_k, omore_sep(`g'))), ws_end),  dnl frick, frigg
	ifelse(`Body parts/functions often used as pejoratives and related:'),
	seq(ws_begin, seq_sep(omore_sep(ns_a), ph_ss, opt(alt(seq_sep(`h', ns_o, ns_l, opt(ns_e)), seq_sep(`h', omore_sep(ns_a), omore_sep(`t')), seq_sep(`w', omore_sep(ns_i), ph_p, omore_sep(ns_e)), seq_sep(`m', alt(`o', `u'), `n', ph_k, opt(`e'), `y'), seq_sep(ph_f, ns_a, alt(seq_sep(`c', ns_e), seq_sep(ns_i, `c')))))), ws_end),  dnl ass[hole|hat|wipe|monkey|face]
	seq(ws_begin, seq_sep(omore_sep(ns_a), `r', omore_sep(`s'), ns_e), ws_end),  dnl arse
	seq(ws_begin, seq_sep(ns_a, `n', omore_sep(`u'), omore_sep(`s')), ws_end),  dnl anus
	seq(ws_begin, seq_sep(opt(seq_sep(omore_sep(ph_b), `u', omore_sep(ns_l))), `s', omore_sep(`h'), ns_i, omore_sep(`t'), zmore_sep(`s')), ws_end),  dnl shit[s]
	seq(seq_sep(ph_k, omore_sep(`r'), omore_sep(ns_a), omore_sep(ph_p)), ws_end),  dnl crap (but not craps)
	seq_sep(omore_sep(alt(ph_p, ph_b)), omore_sep(ns_e), omore_sep(alt(`n', ph_p)), omore_sep(ns_i), omore_sep(alt(`s', `z'))),  dnl penis, bepis
	seq_sep(`v', ns_a, omore_sep(`g'), omore_sep(ns_i), `n', ns_a),  dnl vagina
	seq_sep(ph_k, omore_sep(`u'), omore_sep(`n'), omore_sep(`t')),  dnl cunt
	seq(ws_begin, seq_sep(ph_k, ns_o, ph_k, opt(alt(seq_sep(`h', ns_e, opt(ns_a), `d'), seq_sep(`s', omore_sep(`u'), ph_k, opt(seq_sep(omore_sep(ns_e), omore_sep(`r'))))))), ws_end),  dnl cock[head|sucker]
	ifelse(`Racially-charged words:'),
	seq_sep(`n', ns_i, rep_sep(alt(`g', ph_b, ph_p), `2', `'), alt(`a', seq_sep(zmore_sep(alt(`e', `u')), omore_sep(`r'))), zmore_sep(`s')),  dnl nigg[er|a], nibba etc.
	seq(ws_begin, seq_sep(`j', ns_a, ph_p, opt(`s')), ws_end),  dnl jap
	ifelse(`Sexually-charged words:'),
	seq_sep(ph_b, omore_sep(ns_i), zmore_sep(`y'), zmore_sep(alt(ns_a, ns_o)), ph_ch),  dnl bitch, beyotch, biatch etc.
	seq_sep(ph_f, ns_a, omore_sep(`g'), opt(alt(ns_i, ns_o), omore_sep(`t'))),  dnl fag, fagg[ot|it] etc.
	seq_sep(`w', `h', omore_sep(ns_o), `r', zmore_sep(ns_e)),  dnl whore
`'))', `		')
