from taskiq.cli.worker.args import WorkerArgs
from taskiq.cli.worker.run import run_worker


def main() -> None:
    args = WorkerArgs.from_cli(["broker:broker", "broker.tasks"])
    status = run_worker(args)
    if status is not None:
        raise SystemExit(status)


if __name__ == "__main__":
    main()
