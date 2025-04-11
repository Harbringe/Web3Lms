import { useState } from "react";
import { useRouter } from "next/router";
import BaseHeader from "../partials/BaseHeader";
import BaseFooter from "../partials/BaseFooter";
import apiInstance from "../../utils/axios";
import Toast from "../plugin/Toast";

const CreateNewPassword: React.FC = () => {
  const [password, setPassword] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const router = useRouter();
  const { otp, uuidb64, refresh_token } = router.query;

  const handleCreatePassword = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);

    if (confirmPassword !== password) {
      Toast().fire({
        icon: "warning",
        title: "Passwords do not match",
      });
      setIsLoading(false);
      return;
    }

    const formdata = new FormData();
    formdata.append("password", password);
    if (otp && uuidb64 && refresh_token) {
      formdata.append("otp", otp as string);
      formdata.append("uuidb64", uuidb64 as string);
      formdata.append("refresh_token", refresh_token as string);
    }

    try {
      const res = await apiInstance.post("user/password-change/", formdata);
      console.log(res.data);
      setIsLoading(false);
      router.push("/login");
      Toast().fire({
        icon: "success",
        title: res.data.message,
      });
    } catch (error) {
      console.error(error);
      setIsLoading(false);
    }
  };

  return (
    <>
      <BaseHeader />
      <section className="container d-flex flex-column vh-100" style={{ marginTop: "150px" }}>
        <div className="row align-items-center justify-content-center g-0 h-lg-100 py-8">
          <div className="col-lg-5 col-md-8 py-8 py-xl-0">
            <div className="card shadow">
              <div className="card-body p-6">
                <div className="mb-4">
                  <h1 className="mb-1 fw-bold">Create New Password</h1>
                  <span>Choose a new password for your account</span>
                </div>
                <form className="needs-validation" noValidate onSubmit={handleCreatePassword}>
                  <div className="mb-3">
                    <label htmlFor="password" className="form-label">Enter New Password</label>
                    <input
                      type="password"
                      id="password"
                      className="form-control"
                      name="password"
                      placeholder="**************"
                      required
                      onChange={(e) => setPassword(e.target.value)}
                    />
                    <div className="invalid-feedback">Please enter a valid password.</div>
                  </div>

                  <div className="mb-3">
                    <label htmlFor="confirmPassword" className="form-label">Confirm New Password</label>
                    <input
                      type="password"
                      id="confirmPassword"
                      className="form-control"
                      name="confirmPassword"
                      placeholder="**************"
                      required
                      onChange={(e) => setConfirmPassword(e.target.value)}
                    />
                    <div className="invalid-feedback">Please confirm your password.</div>
                  </div>

                  <div className="d-grid">
                    {isLoading ? (
                      <button disabled type="submit" className="btn btn-primary">
                        Processing <i className="fas fa-spinner fa-spin"></i>
                      </button>
                    ) : (
                      <button type="submit" className="btn btn-primary">
                        Save New Password <i className="fas fa-check-circle"></i>
                      </button>
                    )}
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </section>
      <BaseFooter />
    </>
  );
};

export default CreateNewPassword;
