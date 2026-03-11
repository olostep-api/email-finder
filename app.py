from src.frontend import APP_CSS, build_demo, parse_args

demo = build_demo()


def main() -> None:
    args = parse_args()
    demo.queue(default_concurrency_limit=1)
    demo.launch(server_name=args.host, server_port=args.port, share=args.share, css=APP_CSS)


if __name__ == "__main__":
    main()
