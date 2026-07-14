/* Baby Buddy Dashboard
 *
 * Provides a "watch" function to update the dashboard at one minute intervals
 * and/or on visibility state changes.
 */
BabyBuddy.Dashboard = (function ($) {
  var runIntervalId = null;
  var dashboardElement = null;
  var hidden = null;

  var Dashboard = {
    watch: function (element_id, refresh_rate) {
      dashboardElement = $("#" + element_id);

      if (dashboardElement.length == 0) {
        console.error("Baby Buddy: Dashboard element not found.");
        return false;
      }

      if (typeof document.hidden !== "undefined") {
        hidden = "hidden";
      } else if (typeof document.msHidden !== "undefined") {
        hidden = "msHidden";
      } else if (typeof document.webkitHidden !== "undefined") {
        hidden = "webkitHidden";
      }

      // Refresh only on the configured interval, and (where supported) only
      // while the page is actually visible.
      //
      // We intentionally do NOT reload on the window "focus" event. In the
      // installed / home-screen web app that event fires every single time the
      // app is reopened, which triggered a jarring full-page reload (white
      // flash + scroll reset) on every visit. The interval below still keeps
      // the data fresh at the user's chosen "Refresh rate" (or not at all when
      // it is disabled).
      if (refresh_rate) {
        if (
          typeof window.addEventListener === "undefined" ||
          typeof document.hidden === "undefined"
        ) {
          runIntervalId = setInterval(this.update, refresh_rate);
        } else {
          runIntervalId = setInterval(
            Dashboard.handleVisibilityChange,
            refresh_rate,
          );
        }
      }
    },

    handleVisibilityChange: function () {
      if (!document[hidden]) {
        Dashboard.update();
      }
    },

    update: function () {
      // TODO: Someday maybe update in place?
      location.reload();
    },
  };

  return Dashboard;
})(jQuery);
