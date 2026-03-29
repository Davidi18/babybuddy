if (typeof jQuery === "undefined") {
  throw new Error("Baby Buddy requires jQuery.");
}

/**
 * Baby Buddy Namespace
 *
 * Default namespace for the Baby Buddy app.
 *
 * @type {{}}
 */
var BabyBuddy = (function () {
  return {};
})();

/**
 * Pull to refresh.
 *
 * @type {{init: BabyBuddy.PullToRefresh.init, onRefresh: BabyBuddy.PullToRefresh.onRefresh}}
 */
BabyBuddy.PullToRefresh = (function (ptr) {
  return {
    init: function () {
      ptr.init({
        mainElement: "body",
        onRefresh: this.onRefresh,
      });
    },

    onRefresh: function () {
      window.location.reload();
    },
  };
})(PullToRefresh);

/**
 * Fix for duplicate form submission from double pressing submit
 */
function preventDoubleSubmit() {
  return false;
}
$("form").off("submit", preventDoubleSubmit);
$("form").on("submit", function () {
  $(this).on("submit", preventDoubleSubmit);
});

/**
 * Auto-dismiss toast notifications
 */
(function () {
  var overlay = document.getElementById("bb-toast-overlay");
  if (!overlay) return;

  function dismiss() {
    overlay.classList.add("bb-toast-hiding");
    setTimeout(function () {
      overlay.remove();
    }, 350);
  }

  overlay.addEventListener("click", dismiss);
  setTimeout(dismiss, 2500);
})();

BabyBuddy.RememberAdvancedToggle = function (ptr) {
  localStorage.setItem("advancedForm", event.newState);
};

(function toggleAdvancedFields() {
  window.addEventListener("load", function () {
    if (localStorage.getItem("advancedForm") !== "open") {
      return;
    }

    document.querySelectorAll(".advanced-fields").forEach(function (node) {
      node.open = true;
    });
  });
})();
