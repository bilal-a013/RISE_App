"""RISE Topic Map — Edexcel GCSE Maths (1MA1)

All Foundation and Higher subtopics sourced from the Edexcel specification.
Used by generate_lesson.py and batch_generate.py.
"""

FOUNDATION_TOPICS: dict[str, dict] = {
    "1.1":  {"tier": "foundation", "topic": "Number", "subtopic": "Order of Operations (BIDMAS)"},
    "1.2":  {"tier": "foundation", "topic": "Number", "subtopic": "Place Value & Integers"},
    "1.3":  {"tier": "foundation", "topic": "Number", "subtopic": "The Four Operations"},
    "1.4":  {"tier": "foundation", "topic": "Number", "subtopic": "Prime Factorisation, HCF & LCM"},
    "1.5":  {"tier": "foundation", "topic": "Number", "subtopic": "Fractions"},
    "1.6":  {"tier": "foundation", "topic": "Number", "subtopic": "Decimals"},
    "1.7":  {"tier": "foundation", "topic": "Number", "subtopic": "Percentages"},
    "1.8":  {"tier": "foundation", "topic": "Number", "subtopic": "Rounding (d.p. and s.f.)"},
    "1.9":  {"tier": "foundation", "topic": "Number", "subtopic": "Error Intervals & Bounds (Foundation)"},
    "2.1":  {"tier": "foundation", "topic": "Algebra", "subtopic": "Algebraic Notation & Vocabulary"},
    "2.2":  {"tier": "foundation", "topic": "Algebra", "subtopic": "Substitution"},
    "2.3":  {"tier": "foundation", "topic": "Algebra", "subtopic": "Simplifying & Collecting Like Terms"},
    "2.4":  {"tier": "foundation", "topic": "Algebra", "subtopic": "Expanding Brackets"},
    "2.5":  {"tier": "foundation", "topic": "Algebra", "subtopic": "Factorising (including x2+bx+c)"},
    "2.6":  {"tier": "foundation", "topic": "Algebra", "subtopic": "Solving Linear Equations"},
    "2.7":  {"tier": "foundation", "topic": "Algebra", "subtopic": "Linear Simultaneous Equations"},
    "2.8":  {"tier": "foundation", "topic": "Algebra", "subtopic": "Linear Inequalities"},
    "2.9":  {"tier": "foundation", "topic": "Algebra", "subtopic": "Straight Line Graphs (y=mx+c)"},
    "2.10": {"tier": "foundation", "topic": "Algebra", "subtopic": "Quadratic, Cubic & Reciprocal Graphs"},
    "3.1":  {"tier": "foundation", "topic": "Ratio, Proportion & Rates of Change", "subtopic": "Ratio & Dividing into a Ratio"},
    "3.2":  {"tier": "foundation", "topic": "Ratio, Proportion & Rates of Change", "subtopic": "Scale Factors & Maps"},
    "3.3":  {"tier": "foundation", "topic": "Ratio, Proportion & Rates of Change", "subtopic": "Direct Proportion"},
    "3.4":  {"tier": "foundation", "topic": "Ratio, Proportion & Rates of Change", "subtopic": "Inverse Proportion"},
    "3.5":  {"tier": "foundation", "topic": "Ratio, Proportion & Rates of Change", "subtopic": "Compound Units (Speed, Density, Pressure)"},
    "4.1":  {"tier": "foundation", "topic": "Geometry & Measures", "subtopic": "Angle Facts & Parallel Lines"},
    "4.2":  {"tier": "foundation", "topic": "Geometry & Measures", "subtopic": "Properties of 2D Shapes"},
    "4.3":  {"tier": "foundation", "topic": "Geometry & Measures", "subtopic": "Perimeter, Area & Volume"},
    "4.4":  {"tier": "foundation", "topic": "Geometry & Measures", "subtopic": "Ruler & Compass Constructions"},
    "4.5":  {"tier": "foundation", "topic": "Geometry & Measures", "subtopic": "Transformations"},
    "4.6":  {"tier": "foundation", "topic": "Geometry & Measures", "subtopic": "Pythagoras' Theorem"},
    "4.7":  {"tier": "foundation", "topic": "Geometry & Measures", "subtopic": "Trigonometry (sin, cos, tan)"},
    "5.1":  {"tier": "foundation", "topic": "Probability", "subtopic": "Basic Probability"},
    "5.2":  {"tier": "foundation", "topic": "Probability", "subtopic": "Combined Events"},
    "5.3":  {"tier": "foundation", "topic": "Probability", "subtopic": "Venn Diagrams"},
    "5.4":  {"tier": "foundation", "topic": "Probability", "subtopic": "Tree Diagrams"},
    "6.1":  {"tier": "foundation", "topic": "Statistics", "subtopic": "Charts & Diagrams"},
    "6.2":  {"tier": "foundation", "topic": "Statistics", "subtopic": "Averages & Range"},
}

HIGHER_TOPICS: dict[str, dict] = {
    "1H.1": {"tier": "higher", "topic": "Number", "subtopic": "Product Rule for Counting"},
    "1H.2": {"tier": "higher", "topic": "Number", "subtopic": "Estimating Powers & Roots"},
    "1H.3": {"tier": "higher", "topic": "Number", "subtopic": "Surds & Rationalising Denominators"},
    "1H.4": {"tier": "higher", "topic": "Number", "subtopic": "Upper & Lower Bounds"},
    "2H.1": {"tier": "higher", "topic": "Algebra", "subtopic": "Factorising ax2+bx+c"},
    "2H.2": {"tier": "higher", "topic": "Algebra", "subtopic": "Composite & Inverse Functions"},
    "2H.3": {"tier": "higher", "topic": "Algebra", "subtopic": "Perpendicular Lines"},
    "2H.4": {"tier": "higher", "topic": "Algebra", "subtopic": "Linear & Quadratic Simultaneous Equations"},
    "2H.5": {"tier": "higher", "topic": "Algebra", "subtopic": "Iteration"},
    "3H.1": {"tier": "higher", "topic": "Ratio, Proportion & Rates of Change", "subtopic": "Gradient as Rate of Change"},
    "3H.2": {"tier": "higher", "topic": "Ratio, Proportion & Rates of Change", "subtopic": "Growth & Decay"},
    "4H.1": {"tier": "higher", "topic": "Geometry & Measures", "subtopic": "Circle Theorems"},
    "4H.2": {"tier": "higher", "topic": "Geometry & Measures", "subtopic": "Sine & Cosine Rules"},
    "4H.3": {"tier": "higher", "topic": "Geometry & Measures", "subtopic": "Vectors"},
    "5H.1": {"tier": "higher", "topic": "Statistics & Probability", "subtopic": "Conditional Probability"},
    "5H.2": {"tier": "higher", "topic": "Statistics & Probability", "subtopic": "Histograms"},
    "5H.3": {"tier": "higher", "topic": "Statistics & Probability", "subtopic": "Cumulative Frequency"},
}

ALL_TOPICS: dict[str, dict] = {**FOUNDATION_TOPICS, **HIGHER_TOPICS}
