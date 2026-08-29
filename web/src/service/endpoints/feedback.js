import api from "@/service/api";

export const createFeedback = async (payload) => {
  const response = await api.post("users/feedback/new/", payload);
  return response.data;
};
