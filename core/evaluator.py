import datetime
import json
import multiprocessing
import pathlib

from core import evaluator_config, genetic_algorithm, scale_functions, selection_algorithms, utils


class Evaluator:
    def __init__(self, config: evaluator_config.EvaluatorConfig, cpu_count: int = None):
        self._config: evaluator_config.EvaluatorConfig = config
        self._writing_dir: pathlib.Path = pathlib.Path(f"./{self._config.writing_dir}/data")

        self._writing_dir.mkdir(parents=True, exist_ok=True)

        self._cpu_count = cpu_count or multiprocessing.cpu_count()

    def _write_report(self, name, data):
        with open(self._writing_dir / f'{name}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def _evaluate_experiment(
            self, fitness_fn: evaluator_config.FitnessFunctionConfig, n: int, epochs: int, max_iteration: int
    ):
        report_data = []

        fn = fitness_fn.handler(**fitness_fn.values)
        stats_mode = fitness_fn.stats_mode
        length = fitness_fn.length

        generator = fitness_fn.generator(n=n, length=length, optimal=True)

        for epoch in range(epochs):
            run_data = {}

            population = generator.generate_population()

            for selection_fn in self._config.selection_fns:
                print(
                    f"Fitting GA: epoch={epoch}, n={n}, fitness={fitness_fn.name}, "
                    f"linear(beta={selection_fn.beta}, modified={selection_fn.modified})"
                )

                algo = genetic_algorithm.GeneticAlgorithm(
                    base_population=population,
                    fitness_function=fn,
                    scale_function=scale_functions.LinearRank(selection_fn.beta, n),
                    selection_algo=selection_algorithms.my_sus,
                    stats_mode=stats_mode,
                    modified_selection_algo=selection_fn.modified,
                    max_iteration=max_iteration,
                    draw_step=None,
                    draw_total_steps=False,
                )
                algo.fit()

                run_data[f"{selection_fn.beta}${selection_fn.modified}"] = algo.stats

            report_data.append(run_data)

        report_meta = {
            "n": n,
            "epochs": epochs,
            "max_iteration": max_iteration,
            "selection_fns": {
                "beta": list({fn.beta for fn in self._config.selection_fns}),
                "modified": list({fn.modified for fn in self._config.selection_fns})
            },
            "length": length,
            "fitness_fn": fitness_fn.name,
            "fitness_fn_values": fitness_fn.values,
            "stats_mode": stats_mode,
            "data": report_data,
            "total_data": utils.aggregate_runs_data(report_data, stats_mode)
        }
        current_time = datetime.datetime.now().strftime("%d.%m.%yT%H:%M:%S")
        name = f"data${current_time}${n}${fitness_fn.name}${epochs}"
        self._write_report(name, report_meta)

        print(f"Report successfully generated: {name}.json")

    def evaluate(self):
        procs = []

        epochs = self._config.epochs
        max_iteration = self._config.max_iteration

        for n in self._config.n_vals:
            for fitness_fn in self._config.fitness_fns:
                proc = multiprocessing.Process(
                    target=self._evaluate_experiment,
                    args=(fitness_fn, n, epochs, max_iteration)
                )
                procs.append(proc)
                proc.start()

        # complete the processes
        for proc in procs:
            proc.join()


if __name__ == "__main__":
    Evaluator(evaluator_config.get_config([100])).evaluate()