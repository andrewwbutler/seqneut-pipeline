import marimo

__generated_with = "0.17.2"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Aggregate titers across all sera
    Aggregate the titers across all sera.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Setup and read data""")
    return


@app.cell
def _():
    import pickle

    import altair as alt

    import neutcurve

    import pandas as pd

    _ = alt.data_transformers.disable_max_rows()
    return alt, neutcurve, pd, pickle


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""Get variables from `snakemake`:""")
    return


@app.cell
def _(snakemake):
    input_pickles = snakemake.input.pickles
    input_titers = snakemake.input.titers
    output_pickles = snakemake.output.pickles
    output_titers = snakemake.output.titers
    titers_chart_html = snakemake.output.titers_chart
    groups_sera = snakemake.params.groups_sera
    groups = snakemake.params.groups
    viral_strain_plot_order = snakemake.params.viral_strain_plot_order
    return (
        groups,
        groups_sera,
        input_pickles,
        input_titers,
        output_pickles,
        output_titers,
        titers_chart_html,
        viral_strain_plot_order,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""Get the groups ordered by number of sera in each:""")
    return


@app.cell
def _(groups, groups_sera):
    ordered_groups = [
        g
        for (_, g) in sorted(
            [(sum(g == group for (g, _) in groups_sera), group) for group in groups],
            reverse=True,
        )
    ]

    ordered_groups_sera = [
        f"{group} {serum}"
        for group in ordered_groups
        for (g, serum) in sorted(groups_sera)
        if g == group
    ]
    return ordered_groups, ordered_groups_sera


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Write merged titers for each group""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""Get the merged titers and merged `CurveFits` object:""")
    return


@app.cell
def _(
    groups,
    groups_sera,
    input_pickles,
    input_titers,
    neutcurve,
    output_pickles,
    output_titers,
    pd,
    pickle,
):
    assert len(input_titers) == len(input_pickles) == len(groups_sera)
    assert len(groups) == len(output_titers) == len(output_pickles)

    titers = pd.concat([pd.read_csv(f) for f in input_titers], ignore_index=True)
    assert len(titers) == len(titers.groupby(["group", "serum", "virus"]))
    for group, f in zip(groups, output_titers):
        print(f"Writing aggregated titers for {group=} to {f}")
        titers.query("group == @group").to_csv(f, index=False, float_format="%.4g")

    for group, f in zip(groups, output_pickles):
        fits_list = []
        for (g, serum), pickle_f in zip(groups_sera, input_pickles):
            if g == group:
                with open(pickle_f, "rb") as fin:
                    fits_list.append(pickle.load(fin))
        curvefits = neutcurve.CurveFits.combineCurveFits(fits_list)
        print(f"Pickling aggregated `CurveFits` for {group=} to {f}")
        with open(f, "wb") as fout:
            pickle.dump(curvefits, fout)
    return curvefits, titers


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Plot all the titers""")
    return


@app.cell
def _(
    alt,
    curvefits,
    ordered_groups,
    ordered_groups_sera,
    titers,
    titers_chart_html,
    viral_strain_plot_order,
):
    if viral_strain_plot_order is None:
        _viral_strain_plot_order = sorted(curvefits.allviruses)
    else:
        _viral_strain_plot_order = viral_strain_plot_order
        if set(curvefits.allviruses) - set(_viral_strain_plot_order):
            raise ValueError('not all viruses in `viral_strain_plot_order`:\n' + f'set(curvefits.allviruses) - set(viral_strain_plot_order)={set(curvefits.allviruses) - set(_viral_strain_plot_order)!r}')
    viruses = [v for v in _viral_strain_plot_order if v in curvefits.allviruses]
    assert set(viruses) == set(curvefits.allviruses)
    serum_selection = alt.selection_point(fields=['group_serum'], bind='legend', toggle='true', empty=False)
    group_selection = alt.selection_point(fields=['group'], value=None, bind=alt.binding_select(options=[None] + ordered_groups, labels=['all'] + ordered_groups, name='group'))
    base_chart = alt.Chart(titers).transform_calculate(group_serum=alt.datum['group'] + ' ' + alt.datum['serum']).add_params(serum_selection, group_selection).transform_filter(group_selection).encode(alt.X('titer', title='neutralization titer', scale=alt.Scale(nice=False, padding=5, type='log'), axis=alt.Axis(labelOverlap=True))).properties(height=alt.Step(10))
    median_titers_chart = base_chart.encode(alt.Y('virus', title=None, sort=viruses, axis=alt.Axis(labelLimit=500)), color=alt.value('black'), tooltip=['virus', alt.Tooltip('titer', format='.3g')]).transform_aggregate(titer='median(titer)', groupby=['virus']).mark_line(point={'filled': True, 'size': 50}).properties(width=125, title='median titer')
    per_titers_chart = base_chart.encode(alt.Y('virus', title=None, sort=viruses, axis=alt.Axis(labels=False, ticks=False)), alt.Detail('group_serum:N'), alt.Color('group_serum:N', scale=alt.Scale(range=['black', 'black']), legend=alt.Legend(orient='right', columns=1 + int(1.6 * len(ordered_groups_sera)) // len(viruses), symbolLimit=0, symbolFillColor='black', title='serum (click to select)'), sort=ordered_groups_sera), opacity=alt.condition(serum_selection, alt.value(1), alt.value(0.15)), strokeWidth=alt.condition(serum_selection, alt.value(3), alt.value(1)), tooltip=[alt.Tooltip(c, format='.3g') if titers[c].dtype == float else c for c in titers.columns]).mark_line(point={'filled': True, 'size': 20}).properties(width=225, title='per-serum titers')
    titers_chart = alt.hconcat(median_titers_chart, per_titers_chart, spacing=5).configure_axis(grid=False).configure_legend(padding=10, labelOffset=2, columnPadding=8, labelLimit=400).properties(title=alt.TitleParams('Interactive chart of serum neutralization titers', subtitle=['Median titers are at left; per-serum titers are at right.', 'Mouseover points for details.', 'Click points on serum legend at right to select sera to bold on per-serum chart.', 'Use dropdown at bottom to select serum groups to show.'], fontSize=15, dx=100, dy=-5), autosize=alt.AutoSizeParams(resize=True))
    print(f'Saving chart to {titers_chart_html}')
    titers_chart.save(titers_chart_html)
    titers_chart
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
