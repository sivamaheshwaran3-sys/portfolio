// Contact form: posts JSON to the Flask API and shows the result inline.
(function () {
  var form = document.getElementById("contact-form");
  if (!form) return;
  var status = document.getElementById("form-status");
  var button = form.querySelector("button[type=submit]");

  function show(msg, ok) {
    status.textContent = msg;
    status.className = ok ? "ok" : "err";
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var data = {
      name: form.name.value.trim(),
      email: form.email.value.trim(),
      message: form.message.value.trim()
    };
    if (!data.name || !data.email || !data.message) {
      show("Please fill in all fields.", false);
      return;
    }
    button.disabled = true;
    show("Sending…", true);

    fetch("/api/contact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    })
      .then(function (res) {
        return res.json().then(function (body) { return { ok: res.ok, body: body }; });
      })
      .then(function (r) {
        if (r.ok) {
          form.reset();
          show("Thanks! Your message has been sent.", true);
        } else {
          show(r.body.error || "Something went wrong.", false);
        }
      })
      .catch(function () { show("Network error. Please try again.", false); })
      .finally(function () { button.disabled = false; });
  });
})();
