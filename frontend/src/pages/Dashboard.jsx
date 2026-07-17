import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";

const statusNames = {
  pending: "Gözləyir",
  accepted: "Təsdiqlənib",
  rejected: "Rədd edilib",
  completed: "Tamamlanıb",
  cancelled: "Ləğv edilib",
};

function Dashboard() {
  const navigate = useNavigate();
  const noticeTimerRef = useRef(null);
  const today = new Date().toISOString().split("T")[0];

  const [activeTab, setActiveTab] = useState("dashboard");
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState(null);
  const [mentors, setMentors] = useState([]);
  const [myBookings, setMyBookings] = useState([]);
  const [myReviews, setMyReviews] = useState([]);
  const [mentorProfile, setMentorProfile] = useState(null);
  const [mentorBookings, setMentorBookings] = useState([]);

  const [search, setSearch] = useState("");
  const [dates, setDates] = useState({});
  const [bookingMentorId, setBookingMentorId] = useState(null);

  const [mentorForm, setMentorForm] = useState({
    name: "",
    expertise: "",
    bio: "",
    hourly_rate: "",
  });

  const [reviewForms, setReviewForms] = useState({});

  const [aiForm, setAiForm] = useState({
    goal: "",
    level: "Beginner",
    duration_months: 3,
    weekly_hours: 8,
    budget: 40,
  });

  const [aiPlan, setAiPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState("");
  const [notice, setNotice] = useState(null);

  const showNotice = (text, type = "success") => {
    setNotice({ text, type });

    if (noticeTimerRef.current) {
      window.clearTimeout(noticeTimerRef.current);
    }

    noticeTimerRef.current = window.setTimeout(() => {
      setNotice(null);
      noticeTimerRef.current = null;
    }, 4500);
  };

  useEffect(() => {
    return () => {
      if (noticeTimerRef.current) {
        window.clearTimeout(noticeTimerRef.current);
      }
    };
  }, []);

  const loadMentorArea = async () => {
    try {
      const profileResponse = await api.get("/mentors/mine");
      setMentorProfile(profileResponse.data);

      setMentorForm({
        name: profileResponse.data.name || "",
        expertise: profileResponse.data.expertise || "",
        bio: profileResponse.data.bio || "",
        hourly_rate: profileResponse.data.hourly_rate || "",
      });

      const bookingsResponse = await api.get(
        "/bookings/mentor/my-bookings"
      );

      setMentorBookings(bookingsResponse.data);
    } catch (error) {
      if (error.response?.status === 404) {
        setMentorProfile(null);
        setMentorBookings([]);
        return;
      }

      console.error(error);
    }
  };

  useEffect(() => {
    let cancelled = false;

    const initializeDashboard = async () => {
      try {
        const [
          userResponse,
          statsResponse,
          mentorsResponse,
          bookingsResponse,
          reviewsResponse,
        ] = await Promise.all([
          api.get("/users/me"),
          api.get("/dashboard/user"),
          api.get("/mentors/?limit=100"),
          api.get("/bookings/"),
          api.get("/reviews/my"),
        ]);

        if (cancelled) return;

        setUser(userResponse.data);
        setStats(statsResponse.data);
        setMentors(mentorsResponse.data);
        setMyBookings(bookingsResponse.data);
        setMyReviews(reviewsResponse.data);

        try {
          const profileResponse = await api.get("/mentors/mine");

          if (cancelled) return;

          setMentorProfile(profileResponse.data);

          setMentorForm({
            name: profileResponse.data.name || "",
            expertise: profileResponse.data.expertise || "",
            bio: profileResponse.data.bio || "",
            hourly_rate: profileResponse.data.hourly_rate || "",
          });

          const mentorBookingsResponse = await api.get(
            "/bookings/mentor/my-bookings"
          );

          if (!cancelled) {
            setMentorBookings(mentorBookingsResponse.data);
          }
        } catch (mentorError) {
          if (cancelled) return;

          if (mentorError.response?.status === 404) {
            setMentorProfile(null);
            setMentorBookings([]);
          } else {
            console.error(mentorError);
          }
        }
      } catch (error) {
        if (!cancelled) {
          setNotice({
            text:
              error.response?.data?.detail ||
              "M?lumatlar y?kl?n?rk?n x?ta ba? verdi.",
            type: "error",
          });
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    void initializeDashboard();

    return () => {
      cancelled = true;
    };
  }, []);

  const refreshMentors = async () => {
    const response = await api.get("/mentors/?limit=100");
    setMentors(response.data);
  };

  const refreshMyBookings = async () => {
    const [bookingsResponse, statsResponse, reviewsResponse] =
      await Promise.all([
        api.get("/bookings/"),
        api.get("/dashboard/user"),
        api.get("/reviews/my"),
      ]);

    setMyBookings(bookingsResponse.data);
    setStats(statsResponse.data);
    setMyReviews(reviewsResponse.data);
  };

  const filteredMentors = useMemo(() => {
    const value = search.trim().toLowerCase();

    return mentors.filter((mentor) => {
      if (mentor.owner_id === user?.id) {
        return false;
      }

      if (!value) {
        return true;
      }

      return `${mentor.name} ${mentor.expertise} ${mentor.bio || ""}`
        .toLowerCase()
        .includes(value);
    });
  }, [mentors, search, user]);

  const upcomingBookings = useMemo(
    () =>
      myBookings.filter(
        (booking) =>
          booking.status === "pending" ||
          booking.status === "accepted"
      ),
    [myBookings]
  );

  const handleBooking = async (mentorId) => {
    const bookingDate = dates[mentorId];

    if (!bookingDate) {
      showNotice("Əvvəlcə görüş tarixini seçin.", "error");
      return;
    }

    setBookingMentorId(mentorId);

    try {
      await api.post("/bookings/", {
        mentor_id: mentorId,
        booking_date: bookingDate,
      });

      setDates((current) => ({
        ...current,
        [mentorId]: "",
      }));

      await refreshMyBookings();

      showNotice("Görüş sorğusu uğurla yaradıldı.");
      setActiveTab("bookings");
    } catch (error) {
      showNotice(
        error.response?.data?.detail ||
          "Booking yaradılarkən xəta baş verdi.",
        "error"
      );
    } finally {
      setBookingMentorId(null);
    }
  };

  const cancelBooking = async (bookingId) => {
    setActionLoading(`cancel-${bookingId}`);

    try {
      await api.put(`/bookings/${bookingId}/cancel`);
      await refreshMyBookings();

      showNotice("Görüş ləğv edildi.");
    } catch (error) {
      showNotice(
        error.response?.data?.detail ||
          "Görüş ləğv edilə bilmədi.",
        "error"
      );
    } finally {
      setActionLoading("");
    }
  };

  const saveMentorProfile = async (event) => {
    event.preventDefault();
    setActionLoading("mentor-profile");

    const payload = {
      name: mentorForm.name.trim(),
      expertise: mentorForm.expertise.trim(),
      bio: mentorForm.bio.trim(),
      hourly_rate: Number(mentorForm.hourly_rate),
    };

    try {
      if (mentorProfile) {
        await api.put(`/mentors/${mentorProfile.id}`, payload);
        showNotice("Mentor profili yeniləndi.");
      } else {
        await api.post("/mentors/", payload);
        showNotice("Mentor profili yaradıldı.");
      }

      await Promise.all([
        loadMentorArea(),
        refreshMentors(),
      ]);
    } catch (error) {
      showNotice(
        error.response?.data?.detail ||
          "Mentor profili yadda saxlanmadı.",
        "error"
      );
    } finally {
      setActionLoading("");
    }
  };

  const updateBookingStatus = async (bookingId, nextStatus) => {
    setActionLoading(`${nextStatus}-${bookingId}`);

    try {
      await api.put(`/bookings/${bookingId}/status`, {
        status: nextStatus,
      });

      await Promise.all([
        loadMentorArea(),
        refreshMyBookings(),
      ]);

      showNotice(
        nextStatus === "accepted"
          ? "Görüş təsdiqləndi."
          : nextStatus === "rejected"
            ? "Görüş rədd edildi."
            : "Görüş tamamlandı."
      );
    } catch (error) {
      showNotice(
        error.response?.data?.detail ||
          "Status dəyişdirilə bilmədi.",
        "error"
      );
    } finally {
      setActionLoading("");
    }
  };

  const submitReview = async (booking) => {
    const form = reviewForms[booking.id] || {
      rating: 5,
      comment: "",
    };

    if (!form.comment?.trim()) {
      showNotice("Rəy mətnini daxil edin.", "error");
      return;
    }

    setActionLoading(`review-${booking.id}`);

    try {
      await api.post("/reviews/", {
        mentor_id: booking.mentor_id,
        rating: Number(form.rating || 5),
        comment: form.comment.trim(),
      });

      setReviewForms((current) => ({
        ...current,
        [booking.id]: {
          rating: 5,
          comment: "",
        },
      }));

      await Promise.all([
        refreshMyBookings(),
        refreshMentors(),
      ]);

      showNotice("Rəyiniz uğurla əlavə edildi.");
    } catch (error) {
      showNotice(
        error.response?.data?.detail ||
          "Rəy əlavə edilə bilmədi.",
        "error"
      );
    } finally {
      setActionLoading("");
    }
  };

  const generateAiPlan = async (event) => {
    event.preventDefault();
    setActionLoading("ai-plan");
    setAiPlan(null);

    try {
      const response = await api.post("/ai/learning-plan", {
        goal: aiForm.goal.trim(),
        level: aiForm.level,
        duration_months: Number(aiForm.duration_months),
        weekly_hours: Number(aiForm.weekly_hours),
        budget: Number(aiForm.budget) || null,
      });

      setAiPlan(response.data);
      showNotice("Fərdi inkişaf planınız hazırlandı.");
    } catch (error) {
      showNotice(
        error.response?.data?.detail ||
          "AI plan yaradıla bilmədi.",
        "error"
      );
    } finally {
      setActionLoading("");
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login");
  };

  const hasReviewedMentor = (mentorId) =>
    myReviews.some(
      (review) => review.mentor_id === mentorId
    );

  if (loading) {
    return (
      <div className="page-loader">
        MentorMind AI yüklənir...
      </div>
    );
  }

  return (
    <main className="dashboard-layout">
      <aside className="sidebar">
        <div className="brand">MentorMind AI</div>

        <nav>
          <button
            className={`nav-item ${
              activeTab === "dashboard" ? "active" : ""
            }`}
            onClick={() => setActiveTab("dashboard")}
          >
            Ana panel
          </button>

          <button
            className={`nav-item ${
              activeTab === "mentors" ? "active" : ""
            }`}
            onClick={() => setActiveTab("mentors")}
          >
            Mentorlar
          </button>

          <button
            className={`nav-item ${
              activeTab === "bookings" ? "active" : ""
            }`}
            onClick={() => setActiveTab("bookings")}
          >
            Görüşlərim
          </button>

          <button
            className={`nav-item ${
              activeTab === "mentor-panel" ? "active" : ""
            }`}
            onClick={() => setActiveTab("mentor-panel")}
          >
            Mentor paneli
          </button>

          <button
            className={`nav-item ${
              activeTab === "ai-plan" ? "active" : ""
            }`}
            onClick={() => setActiveTab("ai-plan")}
          >
            AI inkişaf planı
          </button>
        </nav>

        <button className="logout-button" onClick={logout}>
          Çıxış
        </button>
      </aside>

      <section className="dashboard-content">
        <header className="dashboard-header">
          <div>
            <span className="eyebrow">MentorMind AI</span>
            <h1>Salam, {user?.full_name} 👋</h1>
            <p className="muted">
              İnkişafını, görüşlərini və mentor fəaliyyətini
              bir paneldən idarə et.
            </p>
          </div>

          <div className="user-badge">
            <div className="avatar">
              {user?.full_name?.charAt(0)?.toUpperCase()}
            </div>

            <div>
              <strong>{user?.full_name}</strong>
              <span>{user?.email}</span>
            </div>
          </div>
        </header>

        {notice && (
          <div className={`alert ${notice.type}`}>
            {notice.text}
          </div>
        )}

        {activeTab === "dashboard" && (
          <>
            <section className="stats-grid">
              <article className="stat-card">
                <span>Ümumi görüşlər</span>
                <strong>{stats?.total_bookings || 0}</strong>
              </article>

              <article className="stat-card">
                <span>Gözləyən</span>
                <strong>{stats?.pending_bookings || 0}</strong>
              </article>

              <article className="stat-card">
                <span>Təsdiqlənmiş</span>
                <strong>{stats?.accepted_bookings || 0}</strong>
              </article>

              <article className="stat-card">
                <span>Tamamlanmış</span>
                <strong>{stats?.completed_bookings || 0}</strong>
              </article>
            </section>

            <section className="dashboard-two-column">
              <article className="panel-card">
                <div className="panel-title-row">
                  <div>
                    <span className="eyebrow">
                      Qarşıdakı görüşlər
                    </span>
                    <h2>Görüş planınız</h2>
                  </div>

                  <button
                    className="text-button"
                    onClick={() => setActiveTab("bookings")}
                  >
                    Hamısına bax
                  </button>
                </div>

                {upcomingBookings.length === 0 ? (
                  <div className="compact-empty">
                    Hazırda aktiv görüşünüz yoxdur.
                  </div>
                ) : (
                  <div className="compact-list">
                    {upcomingBookings.slice(0, 4).map((booking) => (
                      <div
                        className="compact-list-item"
                        key={booking.id}
                      >
                        <div>
                          <strong>{booking.mentor_name}</strong>
                          <span>
                            {booking.mentor_expertise}
                          </span>
                        </div>

                        <div className="compact-list-right">
                          <strong>{booking.booking_date}</strong>
                          <span
                            className={`status-badge ${booking.status}`}
                          >
                            {statusNames[booking.status]}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </article>

              <article className="panel-card ai-promo-card">
                <span className="eyebrow">AI köməkçi</span>
                <h2>Fərdi inkişaf planı yarat</h2>
                <p>
                  Məqsədini yaz, sistem sənə mərhələli
                  öyrənmə planı və uyğun mentorlar hazırlasın.
                </p>

                <button
                  className="primary-button"
                  onClick={() => setActiveTab("ai-plan")}
                >
                  AI plan yarat
                </button>
              </article>
            </section>
          </>
        )}

        {activeTab === "mentors" && (
          <>
            <section className="section-heading">
              <div>
                <span className="eyebrow">Mentor kataloqu</span>
                <h2>Sizə uyğun mentoru seçin</h2>
              </div>

              <input
                className="search-input"
                placeholder="Python, React, dizayn..."
                value={search}
                onChange={(event) =>
                  setSearch(event.target.value)
                }
              />
            </section>

            {filteredMentors.length === 0 ? (
              <div className="empty-state">
                <h3>Mentor tapılmadı</h3>
                <p>Axtarış sözünü dəyişərək yenidən yoxlayın.</p>
              </div>
            ) : (
              <section className="mentor-grid">
                {filteredMentors.map((mentor) => (
                  <article
                    className="mentor-card"
                    key={mentor.id}
                  >
                    <div className="mentor-top">
                      <div className="mentor-avatar">
                        {mentor.name.charAt(0).toUpperCase()}
                      </div>

                      <div>
                        <h3>{mentor.name}</h3>
                        <span>{mentor.expertise}</span>
                      </div>
                    </div>

                    <p>
                      {mentor.bio ||
                        "Mentor haqqında məlumat yoxdur."}
                    </p>

                    <div className="mentor-meta">
                      <span>
                        ⭐{" "}
                        {mentor.average_rating
                          ? mentor.average_rating
                          : "Yeni"}
                        {mentor.reviews_count
                          ? ` (${mentor.reviews_count})`
                          : ""}
                      </span>

                      <strong>
                        {mentor.hourly_rate} AZN / saat
                      </strong>
                    </div>

                    <div className="booking-row">
                      <input
                        type="date"
                        min={today}
                        value={dates[mentor.id] || ""}
                        onChange={(event) =>
                          setDates((current) => ({
                            ...current,
                            [mentor.id]: event.target.value,
                          }))
                        }
                      />

                      <button
                        className="primary-button small"
                        disabled={
                          bookingMentorId === mentor.id
                        }
                        onClick={() =>
                          handleBooking(mentor.id)
                        }
                      >
                        {bookingMentorId === mentor.id
                          ? "Göndərilir..."
                          : "Görüş seç"}
                      </button>
                    </div>
                  </article>
                ))}
              </section>
            )}
          </>
        )}

        {activeTab === "bookings" && (
          <>
            <section className="section-heading">
              <div>
                <span className="eyebrow">Rezervasiyalar</span>
                <h2>Mənim görüşlərim</h2>
              </div>

              <button
                className="secondary-button"
                onClick={() => setActiveTab("mentors")}
              >
                Yeni mentor seç
              </button>
            </section>

            {myBookings.length === 0 ? (
              <div className="empty-state">
                <h3>Hələ görüşünüz yoxdur</h3>
                <p>Mentor seçərək ilk görüşünüzü yaradın.</p>
              </div>
            ) : (
              <section className="booking-list">
                {myBookings.map((booking) => {
                  const reviewed = hasReviewedMentor(
                    booking.mentor_id
                  );

                  const reviewForm =
                    reviewForms[booking.id] || {
                      rating: 5,
                      comment: "",
                    };

                  return (
                    <article
                      className="booking-card"
                      key={booking.id}
                    >
                      <div className="booking-card-main">
                        <div className="mentor-avatar">
                          {booking.mentor_name
                            ?.charAt(0)
                            .toUpperCase()}
                        </div>

                        <div className="booking-card-info">
                          <h3>{booking.mentor_name}</h3>
                          <span>
                            {booking.mentor_expertise}
                          </span>

                          <div className="booking-details">
                            <span>
                              📅 {booking.booking_date}
                            </span>
                            <span>
                              💳 {booking.hourly_rate} AZN
                            </span>
                          </div>
                        </div>

                        <span
                          className={`status-badge ${booking.status}`}
                        >
                          {statusNames[booking.status] ||
                            booking.status}
                        </span>
                      </div>

                      {(booking.status === "pending" ||
                        booking.status === "accepted") && (
                        <div className="booking-actions">
                          <button
                            className="danger-button"
                            disabled={
                              actionLoading ===
                              `cancel-${booking.id}`
                            }
                            onClick={() =>
                              cancelBooking(booking.id)
                            }
                          >
                            Görüşü ləğv et
                          </button>
                        </div>
                      )}

                      {booking.status === "completed" &&
                        !reviewed && (
                          <div className="review-box">
                            <h4>Mentoru qiymətləndirin</h4>

                            <div className="review-fields">
                              <select
                                value={reviewForm.rating}
                                onChange={(event) =>
                                  setReviewForms((current) => ({
                                    ...current,
                                    [booking.id]: {
                                      ...reviewForm,
                                      rating:
                                        event.target.value,
                                    },
                                  }))
                                }
                              >
                                <option value="5">
                                  5 ulduz
                                </option>
                                <option value="4">
                                  4 ulduz
                                </option>
                                <option value="3">
                                  3 ulduz
                                </option>
                                <option value="2">
                                  2 ulduz
                                </option>
                                <option value="1">
                                  1 ulduz
                                </option>
                              </select>

                              <input
                                placeholder="Görüş haqqında rəyiniz..."
                                value={reviewForm.comment}
                                onChange={(event) =>
                                  setReviewForms((current) => ({
                                    ...current,
                                    [booking.id]: {
                                      ...reviewForm,
                                      comment:
                                        event.target.value,
                                    },
                                  }))
                                }
                              />

                              <button
                                className="primary-button small"
                                disabled={
                                  actionLoading ===
                                  `review-${booking.id}`
                                }
                                onClick={() =>
                                  submitReview(booking)
                                }
                              >
                                Rəyi göndər
                              </button>
                            </div>
                          </div>
                        )}

                      {booking.status === "completed" &&
                        reviewed && (
                          <div className="review-complete">
                            ✓ Bu mentor üçün rəy yazmısınız.
                          </div>
                        )}
                    </article>
                  );
                })}
              </section>
            )}
          </>
        )}

        {activeTab === "mentor-panel" && (
          <>
            <section className="section-heading">
              <div>
                <span className="eyebrow">Mentor sahəsi</span>
                <h2>
                  {mentorProfile
                    ? "Mentor profiliniz"
                    : "Mentor profilinizi yaradın"}
                </h2>
              </div>
            </section>

            <section className="mentor-panel-grid">
              <form
                className="panel-card mentor-form"
                onSubmit={saveMentorProfile}
              >
                <label>
                  Ad və soyad
                  <input
                    value={mentorForm.name}
                    onChange={(event) =>
                      setMentorForm({
                        ...mentorForm,
                        name: event.target.value,
                      })
                    }
                    required
                  />
                </label>

                <label>
                  İxtisas
                  <input
                    placeholder="Python Backend, UI/UX..."
                    value={mentorForm.expertise}
                    onChange={(event) =>
                      setMentorForm({
                        ...mentorForm,
                        expertise: event.target.value,
                      })
                    }
                    required
                  />
                </label>

                <label>
                  Saatlıq qiymət
                  <input
                    type="number"
                    min="1"
                    step="0.01"
                    value={mentorForm.hourly_rate}
                    onChange={(event) =>
                      setMentorForm({
                        ...mentorForm,
                        hourly_rate: event.target.value,
                      })
                    }
                    required
                  />
                </label>

                <label>
                  Haqqınızda
                  <textarea
                    rows="6"
                    placeholder="Təcrübəniz və öyrətdiyiniz mövzular..."
                    value={mentorForm.bio}
                    onChange={(event) =>
                      setMentorForm({
                        ...mentorForm,
                        bio: event.target.value,
                      })
                    }
                    required
                  />
                </label>

                <button
                  className="primary-button"
                  disabled={
                    actionLoading === "mentor-profile"
                  }
                >
                  {mentorProfile
                    ? "Profili yenilə"
                    : "Mentor profili yarat"}
                </button>
              </form>

              <article className="panel-card">
                <span className="eyebrow">Məlumat</span>
                <h2>Mentor imkanları</h2>

                <ul className="feature-list">
                  <li>Platformada mentor kimi görünmək</li>
                  <li>Görüş sorğularını qəbul etmək</li>
                  <li>Görüşləri tamamlanmış kimi işarələmək</li>
                  <li>Reytinq və rəylər toplamaq</li>
                  <li>Şəxsi mentor profilini redaktə etmək</li>
                </ul>

                {mentorProfile && (
                  <div className="mentor-profile-summary">
                    <strong>{mentorProfile.name}</strong>
                    <span>{mentorProfile.expertise}</span>
                    <span>
                      ⭐{" "}
                      {mentorProfile.average_rating || "Yeni"} ·{" "}
                      {mentorProfile.reviews_count} rəy
                    </span>
                  </div>
                )}
              </article>
            </section>

            {mentorProfile && (
              <section className="mentor-requests-section">
                <div className="section-heading">
                  <div>
                    <span className="eyebrow">
                      Mentor görüşləri
                    </span>
                    <h2>Gələn sorğular</h2>
                  </div>
                </div>

                {mentorBookings.length === 0 ? (
                  <div className="empty-state">
                    <h3>Yeni sorğu yoxdur</h3>
                    <p>
                      İstifadəçilərin booking sorğuları burada
                      görünəcək.
                    </p>
                  </div>
                ) : (
                  <section className="booking-list">
                    {mentorBookings.map((booking) => (
                      <article
                        className="booking-card"
                        key={booking.id}
                      >
                        <div className="booking-card-main">
                          <div className="avatar">
                            {booking.user_name
                              ?.charAt(0)
                              .toUpperCase()}
                          </div>

                          <div className="booking-card-info">
                            <h3>{booking.user_name}</h3>
                            <span>{booking.user_email}</span>

                            <div className="booking-details">
                              <span>
                                📅 {booking.booking_date}
                              </span>
                              <span>
                                💳 {booking.hourly_rate} AZN
                              </span>
                            </div>
                          </div>

                          <span
                            className={`status-badge ${booking.status}`}
                          >
                            {statusNames[booking.status]}
                          </span>
                        </div>

                        <div className="booking-actions">
                          {booking.status === "pending" && (
                            <>
                              <button
                                className="primary-button small"
                                onClick={() =>
                                  updateBookingStatus(
                                    booking.id,
                                    "accepted"
                                  )
                                }
                              >
                                Qəbul et
                              </button>

                              <button
                                className="danger-button"
                                onClick={() =>
                                  updateBookingStatus(
                                    booking.id,
                                    "rejected"
                                  )
                                }
                              >
                                Rədd et
                              </button>
                            </>
                          )}

                          {booking.status === "accepted" && (
                            <button
                              className="primary-button small"
                              onClick={() =>
                                updateBookingStatus(
                                  booking.id,
                                  "completed"
                                )
                              }
                            >
                              Görüşü tamamla
                            </button>
                          )}
                        </div>
                      </article>
                    ))}
                  </section>
                )}
              </section>
            )}
          </>
        )}

        {activeTab === "ai-plan" && (
          <>
            <section className="section-heading">
              <div>
                <span className="eyebrow">
                  Süni intellekt dəstəyi
                </span>
                <h2>Fərdi inkişaf planı</h2>
              </div>
            </section>

            <section className="ai-layout">
              <form
                className="panel-card ai-form"
                onSubmit={generateAiPlan}
              >
                <label>
                  Məqsədiniz
                  <textarea
                    rows="5"
                    placeholder="Mən Python backend öyrənmək və 3 aya real API hazırlamaq istəyirəm..."
                    value={aiForm.goal}
                    onChange={(event) =>
                      setAiForm({
                        ...aiForm,
                        goal: event.target.value,
                      })
                    }
                    required
                  />
                </label>

                <div className="form-two-column">
                  <label>
                    Hazırkı səviyyə
                    <select
                      value={aiForm.level}
                      onChange={(event) =>
                        setAiForm({
                          ...aiForm,
                          level: event.target.value,
                        })
                      }
                    >
                      <option value="Beginner">
                        Başlanğıc
                      </option>
                      <option value="Intermediate">
                        Orta
                      </option>
                      <option value="Advanced">
                        Yüksək
                      </option>
                    </select>
                  </label>

                  <label>
                    Müddət
                    <select
                      value={aiForm.duration_months}
                      onChange={(event) =>
                        setAiForm({
                          ...aiForm,
                          duration_months:
                            event.target.value,
                        })
                      }
                    >
                      <option value="1">1 ay</option>
                      <option value="2">2 ay</option>
                      <option value="3">3 ay</option>
                      <option value="4">4 ay</option>
                      <option value="6">6 ay</option>
                    </select>
                  </label>
                </div>

                <div className="form-two-column">
                  <label>
                    Həftəlik vaxt
                    <input
                      type="number"
                      min="1"
                      max="80"
                      value={aiForm.weekly_hours}
                      onChange={(event) =>
                        setAiForm({
                          ...aiForm,
                          weekly_hours:
                            event.target.value,
                        })
                      }
                    />
                  </label>

                  <label>
                    Maksimum büdcə
                    <input
                      type="number"
                      min="0"
                      value={aiForm.budget}
                      onChange={(event) =>
                        setAiForm({
                          ...aiForm,
                          budget: event.target.value,
                        })
                      }
                    />
                  </label>
                </div>

                <button
                  className="primary-button"
                  disabled={actionLoading === "ai-plan"}
                >
                  {actionLoading === "ai-plan"
                    ? "Plan hazırlanır..."
                    : "AI plan yarat"}
                </button>
              </form>

              <article className="panel-card ai-result-wrapper">
                {!aiPlan ? (
                  <div className="ai-placeholder">
                    <div className="ai-placeholder-icon">✦</div>
                    <h3>Planınız burada görünəcək</h3>
                    <p>
                      Məqsəd və vaxt məlumatlarını daxil edərək
                      fərdi yol xəritəsi yaradın.
                    </p>
                  </div>
                ) : (
                  <div className="ai-result">
                    <span className="eyebrow">
                      {aiPlan.track}
                    </span>
                    <h2>{aiPlan.goal}</h2>
                    <p>{aiPlan.summary}</p>

                    <div className="timeline">
                      {aiPlan.months.map((month) => (
                        <article
                          className="timeline-item"
                          key={month.month}
                        >
                          <div className="timeline-number">
                            {month.month}
                          </div>

                          <div>
                            <h3>{month.title}</h3>

                            <ul>
                              {month.topics.map((topic) => (
                                <li key={topic}>{topic}</li>
                              ))}
                            </ul>

                            <small>
                              Həftədə {month.weekly_hours} saat ·{" "}
                              {month.task}
                            </small>
                          </div>
                        </article>
                      ))}
                    </div>

                    {aiPlan.recommended_mentors.length > 0 && (
                      <div className="recommended-box">
                        <h3>Tövsiyə olunan mentorlar</h3>

                        {aiPlan.recommended_mentors.map(
                          (mentor) => (
                            <div
                              className="recommended-mentor"
                              key={mentor.id}
                            >
                              <div>
                                <strong>{mentor.name}</strong>
                                <span>{mentor.expertise}</span>
                              </div>

                              <div>
                                <strong>
                                  {mentor.match_score}% uyğun
                                </strong>
                                <span>
                                  {mentor.hourly_rate} AZN/saat
                                </span>
                              </div>
                            </div>
                          )
                        )}
                      </div>
                    )}
                  </div>
                )}
              </article>
            </section>
          </>
        )}
      </section>
    </main>
  );
}

export default Dashboard;
