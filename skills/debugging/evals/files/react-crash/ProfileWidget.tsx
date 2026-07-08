import React, { useEffect, useState } from "react";
import { getCurrentUser } from "../api/auth";

// Shown in the top-right corner after login on every page.
export function ProfileWidget() {
  const [user, setUser] = useState<any>(null);
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    getCurrentUser().then(setUser);
    const t = setInterval(() => setNow(new Date()), 1000);
    // note: no clearInterval here
  }, []);

  if (!user) return <div className="spinner" />;

  return (
    <div className="profile-widget">
      <img src={user.avatarUrl} alt="" />
      <span>{user.name}</span>
      <span className="pw-age">
        Password set {user.passwordUpdatedAt.toLocaleDateString()}
      </span>
    </div>
  );
}
