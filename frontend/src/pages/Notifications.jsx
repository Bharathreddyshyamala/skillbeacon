import {
    useEffect,
    useState,
  } from "react";
  
  import {
    useNavigate,
  } from "react-router";
  
  import {
    apiRequest,
  } from "../api";
  
  
  export default function Notifications() {
    const [notifications, setNotifications] =
      useState([]);
  
    const [unreadCount, setUnreadCount] =
      useState(0);
  
    const [loading, setLoading] =
      useState(true);
  
    const [error, setError] =
      useState("");
  
    const navigate = useNavigate();
  
  
    async function loadNotifications() {
      try {
        setLoading(true);
        setError("");
  
        const data = await apiRequest(
          "/notifications"
        );
  
        setNotifications(
          data.notifications || []
        );
  
        setUnreadCount(
          data.unread_count || 0
        );
  
      } catch (err) {
        setError(
          err.message ||
          "Failed to load notifications."
        );
  
      } finally {
        setLoading(false);
      }
    }
  
  
    useEffect(() => {
      loadNotifications();
    }, []);
  
  
    async function markAsRead(notification) {
      try {
        if (!notification.is_read) {
          await apiRequest(
            `/notifications/${notification.id}/read`,
            {
              method: "PATCH",
            }
          );
        }
  
        if (notification.action_url) {
          navigate(
            notification.action_url
          );
        }
  
        await loadNotifications();
  
      } catch (err) {
        setError(
          err.message ||
          "Failed to update notification."
        );
      }
    }
  
  
    async function markAllAsRead() {
      try {
        await apiRequest(
          "/notifications/read-all",
          {
            method: "PATCH",
          }
        );
  
        await loadNotifications();
  
      } catch (err) {
        setError(
          err.message ||
          "Failed to update notifications."
        );
      }
    }
  
  
    async function deleteNotification(
      notificationId
    ) {
      try {
        await apiRequest(
          `/notifications/${notificationId}`,
          {
            method: "DELETE",
          }
        );
  
        await loadNotifications();
  
      } catch (err) {
        setError(
          err.message ||
          "Failed to delete notification."
        );
      }
    }
  
  
    if (loading) {
      return (
        <div className="container py-4">
          <p>Loading notifications...</p>
        </div>
      );
    }
  
  
    return (
      <div className="container py-4">
  
        <div className="d-flex justify-content-between align-items-center mb-4">
  
          <div>
            <h2>Notifications</h2>
  
            <p className="text-secondary mb-0">
              {unreadCount} unread notification
              {unreadCount !== 1 ? "s" : ""}
            </p>
          </div>
  
          {unreadCount > 0 && (
            <button
              className="btn btn-outline-primary"
              onClick={markAllAsRead}
            >
              Mark all as read
            </button>
          )}
  
        </div>
  
  
        {error && (
          <div className="alert alert-danger">
            {error}
          </div>
        )}
  
  
        {notifications.length === 0 ? (
          <div className="alert alert-secondary">
            You do not have any notifications.
          </div>
        ) : (
  
          <div className="list-group">
  
            {notifications.map(
              (notification) => (
  
                <div
                  key={notification.id}
                  className={
                    `list-group-item ${
                      !notification.is_read
                        ? "border-primary"
                        : ""
                    }`
                  }
                >
  
                  <div className="d-flex justify-content-between">
  
                    <div
                      role="button"
                      onClick={() =>
                        markAsRead(notification)
                      }
                    >
  
                      <h6 className="mb-1">
                        {!notification.is_read && (
                          <span className="me-2">
                            🔵
                          </span>
                        )}
  
                        {notification.title}
                      </h6>
  
                      <p className="mb-1">
                        {notification.message}
                      </p>
  
                      <small className="text-secondary">
                        {new Date(
                          notification.created_at
                        ).toLocaleString()}
                      </small>
  
                    </div>
  
  
                    <button
                      className="btn btn-sm btn-outline-danger"
                      onClick={() =>
                        deleteNotification(
                          notification.id
                        )
                      }
                    >
                      Delete
                    </button>
  
                  </div>
  
                </div>
              )
            )}
  
          </div>
        )}
  
      </div>
    );
  }