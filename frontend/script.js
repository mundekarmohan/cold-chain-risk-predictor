
function showScreen(screenId) {
  document.querySelectorAll(".screen").forEach((screen) => {
    screen.classList.remove("active");
  });

  const target = document.getElementById(screenId);

  if (!target) {
    console.error("Screen not found:", screenId);
    return;
  }

  target.classList.add("active");

  const errorMessage = document.getElementById("errorMessage");
  if (errorMessage) errorMessage.textContent = "";

  window.scrollTo({ top: 0, behavior: "smooth" });
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("predictionForm");
  const predictButton = document.getElementById("predictButton");
  const errorMessage = document.getElementById("errorMessage");

  if (!form || !predictButton) {
    console.error("Prediction form or button is missing.");
    return;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorMessage.textContent = "";

    const payload = {
      Fruit: document.getElementById("Fruit").value,
      Temp: Number(document.getElementById("Temp").value),
      Humid: Number(document.getElementById("Humid").value),
      Light: Number(document.getElementById("Light").value),
      CO2: Number(document.getElementById("CO2").value)
    };

    const numericValues = [
      payload.Temp,
      payload.Humid,
      payload.Light,
      payload.CO2
    ];

    if (
      !payload.Fruit ||
      numericValues.some((value) => !Number.isFinite(value))
    ) {
      errorMessage.textContent =
        "Please enter valid values in every field.";
      return;
    }

    predictButton.disabled = true;
    predictButton.textContent = "Analyzing...";

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error || "Prediction failed. Please try again."
        );
      }

      const prediction = String(data.prediction || "").toLowerCase();
      const isGood = prediction === "good";
      const probabilities = data.probabilities || {};

      const good = Number(
        probabilities.Good ?? probabilities.good ?? 0
      );

      const bad = Number(
        probabilities.Bad ??
        probabilities.BAD ??
        probabilities.bad ??
        0
      );

      document.getElementById("resultSymbol").textContent =
        isGood ? "✓" : "!";

      document.getElementById("resultSymbol").className =
        "result-symbol " + (isGood ? "symbol-good" : "symbol-bad");

      document.getElementById("resultTitle").textContent =
        isGood ? "Good Condition" : "Bad Condition";

      document.getElementById("resultBadge").textContent =
        isGood ? "Lower predicted risk" : "Potential risk detected";

      document.getElementById("resultBadge").className =
        "result-badge " + (isGood ? "" : "badge-bad");

      document.getElementById("resultText").textContent = isGood
        ? "The model classified these storage conditions as Good. Continue monitoring the environment."
        : "The model classified these storage conditions as Bad. Inspect the fruit and review the storage conditions.";

      document.getElementById("goodProbability").textContent =
        good.toFixed(1) + "%";

      document.getElementById("badProbability").textContent =
        bad.toFixed(1) + "%";

      document.getElementById("goodBar").style.width =
        Math.max(0, Math.min(100, good)) + "%";

      document.getElementById("badBar").style.width =
        Math.max(0, Math.min(100, bad)) + "%";

      showScreen("result");
    } catch (error) {
      errorMessage.textContent =
        error.message || "Could not connect to the prediction API.";
    } finally {
      predictButton.disabled = false;
      predictButton.innerHTML = 'Predict Risk <span>→</span>';
    }
  });
});
