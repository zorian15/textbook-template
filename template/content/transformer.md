This chapter is a worked example.
It exists so you can see every feature of the build in one place — callouts, a figure, a citation, and an end-of-chapter quiz — using a topic (the transformer) that any reader of a machine-learning-adjacent book will recognize.
Delete it once your own first chapter is drafted, and use it as a pattern while you write.

The transformer is the architecture underneath nearly every modern foundation model.
It was introduced in a single 2017 paper [@vaswani2017], and its central move — self-attention — is what lets a model relate any two positions in a sequence directly, no matter how far apart they are.

## Self-attention

Self-attention gives every position in a sequence a way to look at every other position and pull in what it needs.
Each position emits a *query*, and every position offers a *key* and a *value*; the query is compared against all keys, the scores are normalized, and the output is the score-weighted sum of the values.

!!! intuition "Intuition"
    Attention is a soft, learned lookup table. Each position asks a question (its query) and gets back a blend of answers (values), weighted by how well each other position's key matches the question.

The cost of that generality is quadratic.
Scoring every query against every key produces an n-by-n matrix for a sequence of length n, so both compute and memory grow with the square of the sequence length — the single fact that most long-context research is trying to work around.

!!! analogy "Analogy"
    Think of a room where everyone can hear everyone at once. Perfect information, but the number of conversations grows with the square of the crowd — which is exactly why large rooms need structure.

<figure class="widget" data-widget="example-slider">
<figcaption>An interactive figure: drag the slider to change the coefficient a and watch the parabola y = a x² — the same square-law growth that makes attention quadratic. This is the template's one worked widget; replace it (and its entry in assets/widgets.js) with figures that fit your book, or delete it if your book has no interactive figures.</figcaption>
</figure>

<figure>
<img src="assets/figures/example-pipeline.svg" alt="Three boxes left to right connected by arrows: an input box, a model box, and an output box.">
<figcaption>A static figure, for comparison: an input, the method under study, and the output it produces. Replace this figure with one that fits your subject.</figcaption>
</figure>

## Putting it together

A single attention pattern is rarely enough, so a transformer runs several in parallel.
Each *head* projects into its own subspace and attends there, letting different heads specialize — one tracking word order, another long-range agreement — before their outputs are concatenated and mixed.

Because attention treats its input as an unordered set, position has to be injected separately, as learned embeddings or fixed sinusoids added to the inputs.
And in a decoder that generates left to right, a *causal mask* hides future positions so that a token being predicted cannot attend to the answer.

!!! probe "Interview"
    *Why does a transformer need positional encodings when a convolution or an RNN does not?*
    Because self-attention is permutation-equivariant: with no positional signal, shuffling the input tokens just shuffles the outputs the same way, and word order carries no information. Convolutions and RNNs bake order into their structure; attention does not, so it must be supplied.

!!! warning "Common trap"
    "More heads is always better" is not true. Heads split the model dimension between them, so past a point you are giving each head too little room to represent anything useful. The right count is a tuning decision, not a maximization.

The rest is assembly: stack these attention-and-feedforward blocks, add residual connections and normalization so gradients flow, and you have the backbone that scales from a small classifier to a frontier model.
