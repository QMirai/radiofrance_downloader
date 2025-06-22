from argparse import ArgumentParser
import threading
from audio import main


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="download audio"
    )

    parser.add_argument('link', type=str,
                        help="link of the web with podcasts")
    parser.add_argument('-p', '--output_path', type=str,
                        default="D:/podcasts",
                        help="output path, default path is D:/podcasts")
    parser.add_argument('-l', "--parallel", default=4,
                        help="parallel download number")
    parser.add_argument('-t', "--test", action="store_true",
                        help="for test")

    args = parser.parse_args()
    main(args.link, args.output_path, args.parallel, args.test)
