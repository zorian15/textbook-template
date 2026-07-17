"""Single source of truth for the end-of-chapter "Check yourself" quizzes.

Each chapter closes with a short set of challenging multiple-choice questions.
`build.py` renders the quiz for a chapter after its References section, and a
small inline script makes it interactive: the reader picks an option, the choice
is marked right or wrong, the correct answer is revealed, and an explanation
appears.

The questions are meant to be *hard* in the way a sharp reviewer's question is
hard. The distractors are plausible misconceptions, stated with the same
confidence and detail as the answer, so that neither length nor specificity ever
signals which option is correct. The renderer shuffles the options on load, so
the position of the answer carries no information either — write the options in
any order and point `answer` at the right one. Each explanation carries a
second-layer detail the prose only gestures at, so the quiz teaches rather than
merely confirms.

Question strings are **plain text**. `build.py` HTML-escapes everything, which
would neutralize MathJax delimiters, so do not write `$...$` or `\\(...\\)`
here; phrase math in words or with plain symbols instead.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Question:
    """One multiple-choice question.

    `options` are shuffled at render time, so their order here does not matter;
    `answer` is the index (into this tuple) of the single correct option.
    `explanation` is revealed after the reader answers and should teach, not
    just confirm. Because the display order is randomized, never write an option
    that refers to another by position (e.g. "same as A").
    """

    prompt: str
    options: tuple[str, ...]
    answer: int
    explanation: str

    def __post_init__(self) -> None:
        assert self.prompt.strip(), "Question has an empty prompt."
        assert len(self.options) >= 3, f"{self.prompt!r}: need at least 3 options."
        assert all(o.strip() for o in self.options), f"{self.prompt!r}: empty option."
        assert (
            0 <= self.answer < len(self.options)
        ), f"{self.prompt!r}: answer index {self.answer} is out of range."
        assert self.explanation.strip(), f"{self.prompt!r}: empty explanation."


# One worked quiz so a drafter has a pattern to copy. Add a tuple of 4-6
# Questions under each chapter's slug as the chapter is drafted; the build
# asserts the 4-6 range and that every slug is a real chapter. Delete this
# example once the first real chapter is drafted.
_QUIZZES: dict[str, tuple[Question, ...]] = {
    "transformer": (
        Question(
            prompt="Self-attention lets every position attend to every other position in a sequence. What is the immediate cost of that design, before any optimization?",
            options=(
                "Compute and memory that grow with the square of the sequence length, because every pair of positions is scored.",
                "Compute that grows linearly with sequence length, because each position looks only at a fixed-size window of neighbors.",
                "A fixed compute cost independent of sequence length, because attention weights are precomputed once per model.",
                "Compute dominated entirely by the depth of the network, with sequence length contributing only a constant factor.",
            ),
            answer=0,
            explanation="Attention scores every query against every key, so an n-token sequence produces an n-by-n matrix: both time and memory scale as n squared. That quadratic term is exactly what long-context methods (sparse, low-rank, or windowed attention) try to reduce; the vanilla mechanism pays it in full.",
        ),
        Question(
            prompt="Why does a plain self-attention layer need positional information injected separately, unlike a convolution or an RNN?",
            options=(
                "Because attention is permutation-equivariant: with no positional signal, shuffling the tokens shuffles the outputs identically and order is lost.",
                "Because attention can only represent local relationships, so absolute position must be supplied to reach distant tokens.",
                "Because the softmax saturates for long sequences unless positions are added to keep the logits in a stable range.",
                "Because positional encodings are what make the model differentiable with respect to the input tokens.",
            ),
            answer=0,
            explanation="Attention treats its input as a set: reorder the tokens and each output is reordered the same way, carrying no notion of who came first. Convolutions and RNNs bake order into their structure; attention does not, so position must be encoded into the inputs (learned embeddings, sinusoids, or rotary phases) for word order to matter.",
        ),
        Question(
            prompt="What problem do multiple attention heads solve that a single, wider head does not?",
            options=(
                "They let the model attend to several different relationships in parallel, each in its own subspace, then combine them.",
                "They reduce the parameter count relative to one wide head while keeping the same expressive power exactly.",
                "They remove the need for positional encodings by giving each head its own coordinate system.",
                "They guarantee that attention weights sum to one across heads, stabilizing training.",
            ),
            answer=0,
            explanation="Each head projects into its own lower-dimensional subspace and computes attention there, so different heads can specialize — one tracking syntax, another coreference, another position — and the concatenation recombines them. A single wide head must express all of that with one shared attention pattern, which is strictly less flexible.",
        ),
        Question(
            prompt="In a decoder-only transformer, what does the causal mask actually enforce, and why is it necessary?",
            options=(
                "Each position may attend only to itself and earlier positions, so the model cannot peek at tokens it is trained to predict.",
                "Each position attends only to a fixed window of recent tokens, bounding the attention cost to a constant.",
                "The mask zeroes out padding tokens so that variable-length sequences can be batched together.",
                "The mask forces attention weights to be symmetric, so information flows equally in both directions.",
            ),
            answer=0,
            explanation="Autoregressive training predicts token t from tokens before it; if position t could attend to t+1, the target would leak into the input and the loss would be trivially minimized. The causal (lower-triangular) mask sets future scores to negative infinity before the softmax, so each position sees only the past. Padding masks exist too, but that is a separate mechanism.",
        ),
    ),
}


def _validate(
    quizzes: dict[str, tuple[Question, ...]],
) -> dict[str, tuple[Question, ...]]:
    """Assert each chapter has 4-6 questions."""
    for slug, questions in quizzes.items():
        assert (
            4 <= len(questions) <= 6
        ), f"Quiz for '{slug}' has {len(questions)} questions; expected 4-6."
    return quizzes


QUIZZES: dict[str, tuple[Question, ...]] = _validate(_QUIZZES)
