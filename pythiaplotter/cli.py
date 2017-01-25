"""Setup commandline interface, process args, and set defaults for those unspecified."""


from __future__ import absolute_import
import argparse
import os.path
import logging
import pythiaplotter.utils.logging_config  # NOQA
import pythiaplotter.utils.common as helpr
from pythiaplotter.parsers import parser_opts
from pythiaplotter.printers import printer_opts_checked, print_printers_requirements
from pythiaplotter import __VERSION__


log = logging.getLogger(__name__)


def get_args(input_args):
    """Get argparse.Namespace of parsed user arguments, with sensible defaults set."""

    parser = argparse.ArgumentParser(
        prog="PythiaPlotter",
        description="Convert MC event into a particle evolution diagram. "
                    "Requires you to choose an input format, and an output printer.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    #################
    # Input options
    #################
    input_group = parser.add_argument_group('Input Options')

    input_group.add_argument("input",
                             help="Input file")

    parser_help = ["Input formats:"]
    for k, v in parser_opts.items():
        help_str = "{0}: {1}".format(k, v.description)
        if v.file_extension:
            help_str += " (default for files ending in {})".format(v.file_extension)
        parser_help.append(help_str)

    input_group.add_argument("--inputFormat",
                             help="\n".join(parser_help),
                             choices=list(parser_opts.keys()))
    input_group.add_argument("-n", "--eventNumber",
                             help="Select event number to plot, starts at 1.\n"
                                  "For: HEPMC, LHE input formats.\n",
                             type=int,
                             default=0)

    #################
    # Output file options
    #################
    output_group = parser.add_argument_group('Output Diagram Options')

    output_group.add_argument("-O", "--output",
                              help="Output diagram filename "
                                   "(if unspecified, defaults to INPUT.pdf)")
    output_group.add_argument("--outputFormat",
                              help="Output diagram file format (defaults to "
                                   "extension given to --output)")
    output_group.add_argument("--open",
                              help="Automatically open diagram once plotted",
                              action="store_true")

    #################
    # Printer options
    #################
    output_group.add_argument("--noOutput",
                              help="Don't convert Graphviz file to diagram",
                              action="store_true")

    printer_help = ["Printing methods:"]
    printer_help.extend(["{0}: {1}".format(k, v.description)
                         for k, v in printer_opts_checked.items()])
    output_group.add_argument("-p", "--printer",
                              help="\n".join(printer_help),
                              choices=list(printer_opts_checked.keys()),
                              default="DOT" if "DOT" in printer_opts_checked else "LATEX")

    output_group.add_argument("--redundants",
                              help="Keep redundant particles (defualt is to remove them)",
                              action="store_true")

    #################
    # Miscellaneous options
    #################
    misc_group = parser.add_argument_group("Miscellaneous Options")

    misc_group.add_argument("-v", "--verbose",
                            help="Print debug statements to screen",
                            action="store_true")
    misc_group.add_argument("--stats",
                            help="Print some statistics about the event/graph",
                            action="store_true")
    misc_group.add_argument('--version', action='version', version='%(prog)s ' + __VERSION__)

    # Handle the scenario where there are no printers available
    if len(printer_opts_checked) == 0:
        parser.print_help()
        log.info("")
        log.error("None of the required programs or python packages "
                  "for any printing option exist.")
        print_printers_requirements(log.info)
        exit(11)

    args = parser.parse_args(input_args)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    args.input = helpr.cleanup_filepath(args.input)  # sanitise input

    if not helpr.check_file_exists(args.input):
        raise IOError("No such file: '%s'" % args.input)

    # Post process user args
    set_default_output_settings(args)
    set_default_input_format(args)
    set_default_mode(args)

    for k, v in args.__dict__.items():
        log.debug("{0}: {1}".format(k, v))

    return args


def set_default_output_settings(args):
    """Set default output filenames and stems/dirs"""
    # TODO: shouldn't be setting args.X here as a side effect!
    stem_name, _ = os.path.splitext(os.path.basename(args.input))
    input_dir = helpr.get_directory(args.input)
    # Set default output format if there is an output filename specified
    if args.output:
        args.output = helpr.cleanup_filepath(args.output)
        if not args.outputFormat:
            args.outputFormat = os.path.splitext(args.output)[1][1:]
            log.info("You didn't specify an output format, "
                     "assuming from output filename that it is %s", args.outputFormat)
    # Set default output filename if not already done
    else:
        # Hmm default hidden here, not good
        if not args.outputFormat:
            args.outputFormat = "pdf"
            log.info("You didn't specify an output format, defaulted to %s", args.outputFormat)
        filename = "".join([stem_name, "_", str(args.eventNumber), ".", args.outputFormat])
        args.output = os.path.join(input_dir, filename)
        log.info("You didn't specify an output filename, setting it to %s", args.output)


def set_default_input_format(args):
    """Set default input format if the user hasn't."""
    if not args.inputFormat:
        for pname, popt in parser_opts.items():
            input_extension = os.path.splitext(args.input)[1]
            if input_extension.lower() == popt.file_extension:
                args.inputFormat = pname
                log.info("You didn't set an input format. Assuming %s" % args.inputFormat)
                break
        else:
            raise RuntimeError("Cannot determine input format. "
                               "Must be one of {}".format(list(parser_opts.keys())))


def set_default_mode(args):
    """Set default particle mode (representation) if the user hasn't."""
    args.particleMode = parser_opts[args.inputFormat].default_representation
    log.info("Using %s particle representation" % args.particleMode)


def print_options(args):
    """Printout for user arguments."""
    for k, v in args.__dict__.items():
        log.info("{0}: {1}".format(k, v))
