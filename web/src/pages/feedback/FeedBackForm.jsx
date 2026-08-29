import { useState } from "react";
import {
  Bug,
  CheckCircle2,
  FileText,
  Lightbulb,
  MessageCircle,
  Send,
  Sparkles,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

import { createFeedback } from "@/service/endpoints/feedback";

const FEEDBACK_TYPES = [
  {
    value: "BUG REPORT",
    label: "Bug Report",
    description: "Report something that is broken or behaving incorrectly.",
    icon: Bug,
  },
  {
    value: "FEATURE REQUEST",
    label: "Feature Request",
    description: "Suggest a new feature or improvement.",
    icon: Lightbulb,
  },
  {
    value: "DOCUMENTATION",
    label: "Documentation",
    description: "Report missing, incorrect, or unclear documentation.",
    icon: FileText,
  },
  {
    value: "USER EXPERIENCE",
    label: "User Experience",
    description: "Share feedback about the overall product experience.",
    icon: Sparkles,
  },
  {
    value: "GENERAL",
    label: "General",
    description: "Anything else you want to share with us.",
    icon: MessageCircle,
  },
];

export default function FeedbackForm() {
  const [feedbackType, setFeedbackType] = useState("BUG REPORT");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [stepsToReproduce, setStepsToReproduce] = useState("");
  const [actualBehavior, setActualBehavior] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");

  const selectedType =
    FEEDBACK_TYPES.find((item) => item.value === feedbackType) ?? FEEDBACK_TYPES[0];

  const SelectedIcon = selectedType.icon;

  const handleSubmit = async (event) => {
    event.preventDefault();

    const trimmedTitle = title.trim();
    const trimmedDescription = description.trim();
    const trimmedSteps = stepsToReproduce.trim();
    const trimmedActual = actualBehavior.trim();

    if (!trimmedTitle || !trimmedDescription) {
      setError("Title and description are required.");
      return;
    }

    if (trimmedTitle.length > 50) {
      setError("Title must be 50 characters or less.");
      return;
    }

    if (trimmedDescription.length > 150) {
      setError("Description must be 150 characters or less.");
      return;
    }

    if (feedbackType === "BUG REPORT") {
      if (!trimmedSteps) {
        setError("Steps to reproduce are required for bug reports.");
        return;
      }

      if (!trimmedActual) {
        setError("Actual behavior is required for bug reports.");
        return;
      }

      if (trimmedSteps.length > 150) {
        setError("Steps to reproduce must be 150 characters or less.");
        return;
      }

      if (trimmedActual.length > 150) {
        setError("Actual behavior must be 150 characters or less.");
        return;
      }
    }

    setSubmitting(true);
    setError("");

    const payload = {
      type_of_feedback: feedbackType,
      title: trimmedTitle,
      description: trimmedDescription,
      steps_to_reproduce: feedbackType === "BUG REPORT" ? trimmedSteps : "",
      actual_behavior: feedbackType === "BUG REPORT" ? trimmedActual : "",
    };

    try {
      await createFeedback(payload);
      setSubmitted(true);
    } catch (submissionError) {
      const responseData = submissionError?.response?.data;

      if (responseData?.detail) {
        setError(responseData.detail);
      } else if (responseData?.title?.[0]) {
        setError(responseData.title[0]);
      } else if (responseData?.description?.[0]) {
        setError(responseData.description[0]);
      } else if (responseData?.steps_to_reproduce?.[0]) {
        setError(responseData.steps_to_reproduce[0]);
      } else if (responseData?.actual_behavior?.[0]) {
        setError(responseData.actual_behavior[0]);
      } else if (responseData?.type_of_feedback?.[0]) {
        setError(responseData.type_of_feedback[0]);
      } else {
        setError("Failed to submit feedback. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
    setSubmitted(false);
    setFeedbackType("BUG REPORT");
    setTitle("");
    setDescription("");
    setStepsToReproduce("");
    setActualBehavior("");
    setError("");
  };

  if (submitted) {
    return (
      <section className="flex min-h-0 flex-1 items-center justify-center rounded-2xl border bg-card p-8 shadow-sm">
        <div className="w-full max-w-lg text-center">
          <div className="mx-auto flex size-12 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-600">
            <CheckCircle2 className="size-6" />
          </div>

          <h2 className="mt-5 text-xl font-bold tracking-tight">Feedback received.</h2>

          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-muted-foreground">
            Thanks for helping improve Mokvio. Your feedback has been recorded and will be reviewed.
          </p>

          <Button type="button" variant="outline" className="mt-6" onClick={resetForm}>
            Submit another
          </Button>
        </div>
      </section>
    );
  }

  return (
    <section className="min-h-0 flex-1 overflow-hidden rounded-2xl border bg-card shadow-sm">
      <div className="grid h-full lg:grid-cols-[0.8fr_1.2fr]">
        <aside className="hidden border-r bg-muted/10 p-5 lg:flex lg:flex-col">
          <div>
            <p className="text-xs font-semibold">What would you like to report?</p>

            <p className="mt-1 text-xs leading-5 text-muted-foreground">
              Choose the category that best describes your feedback.
            </p>
          </div>

          <div className="mt-5 space-y-2">
            {FEEDBACK_TYPES.map((item) => {
              const Icon = item.icon;
              const active = feedbackType === item.value;

              return (
                <button
                  key={item.value}
                  type="button"
                  onClick={() => {
                    setFeedbackType(item.value);
                    setError("");
                  }}
                  className={`flex w-full items-start gap-3 rounded-xl border p-3 text-left transition-colors ${
                    active
                      ? "border-primary/30 bg-primary/5"
                      : "border-transparent hover:border-border hover:bg-muted/40"
                  }`}
                >
                  <div
                    className={`flex size-8 shrink-0 items-center justify-center rounded-lg ${
                      active ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"
                    }`}
                  >
                    <Icon className="size-4" />
                  </div>

                  <div className="min-w-0">
                    <p className="text-xs font-semibold">{item.label}</p>

                    <p className="mt-0.5 text-[11px] leading-4 text-muted-foreground">
                      {item.description}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>

          <div className="mt-auto rounded-xl border border-dashed bg-background/60 p-4">
            <p className="font-mono text-[9px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
              Good feedback
            </p>

            <ul className="mt-2 space-y-1.5 text-[11px] leading-4 text-muted-foreground">
              <li>• Explain what happened.</li>
              <li>• Tell us what you expected.</li>
              <li>• Include reproduction steps for bugs.</li>
              <li>• Keep within the character limits.</li>
            </ul>
          </div>
        </aside>

        <form onSubmit={handleSubmit} className="flex min-h-0 flex-col">
          <div className="min-h-0 flex-1 overflow-y-auto p-5 sm:p-6">
            <div className="lg:hidden">
              <p className="text-xs font-semibold">Feedback type</p>

              <p className="mt-1 text-[11px] text-muted-foreground">
                Select what best describes your feedback.
              </p>

              <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3">
                {FEEDBACK_TYPES.map((item) => {
                  const Icon = item.icon;
                  const active = feedbackType === item.value;

                  return (
                    <button
                      key={item.value}
                      type="button"
                      onClick={() => {
                        setFeedbackType(item.value);
                        setError("");
                      }}
                      className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-left text-xs transition-colors ${
                        active ? "border-primary/30 bg-primary/5 text-primary" : "hover:bg-muted/40"
                      }`}
                    >
                      <Icon className="size-3.5 shrink-0" />

                      <span className="truncate">{item.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {error && (
              <div className="mt-5 rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2.5 text-xs text-destructive">
                {error}
              </div>
            )}

            <div className="mt-5 space-y-2">
              <label htmlFor="title" className="text-xs font-medium">
                Title
              </label>

              <Input
                id="title"
                value={title}
                onChange={(event) => {
                  setTitle(event.target.value);
                  setError("");
                }}
                placeholder="Briefly describe your feedback"
                maxLength={50}
                required
                disabled={submitting}
              />

              <p className="text-right text-[10px] text-muted-foreground">{title.length}/50</p>
            </div>

            <div className="mt-4 space-y-2">
              <label htmlFor="description" className="text-xs font-medium">
                Description
              </label>

              <Textarea
                id="description"
                value={description}
                onChange={(event) => {
                  setDescription(event.target.value);
                  setError("");
                }}
                placeholder="Describe the problem, idea, or feedback."
                className="min-h-28 resize-none"
                maxLength={150}
                required
                disabled={submitting}
              />

              <p className="text-right text-[10px] text-muted-foreground">
                {description.length}/150
              </p>
            </div>

            {feedbackType === "BUG REPORT" && (
              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <label htmlFor="steps" className="text-xs font-medium">
                    Steps to reproduce
                  </label>

                  <Textarea
                    id="steps"
                    value={stepsToReproduce}
                    onChange={(event) => {
                      setStepsToReproduce(event.target.value);
                      setError("");
                    }}
                    placeholder={"1. Open...\n2. Click...\n3. Observe..."}
                    className="min-h-24 resize-none"
                    maxLength={150}
                    required
                    disabled={submitting}
                  />

                  <p className="text-right text-[10px] text-muted-foreground">
                    {stepsToReproduce.length}/150
                  </p>
                </div>

                <div className="space-y-2">
                  <label htmlFor="actual" className="text-xs font-medium">
                    Actual behavior
                  </label>

                  <Textarea
                    id="actual"
                    value={actualBehavior}
                    onChange={(event) => {
                      setActualBehavior(event.target.value);
                      setError("");
                    }}
                    placeholder="What actually happened?"
                    className="min-h-24 resize-none"
                    maxLength={150}
                    required
                    disabled={submitting}
                  />

                  <p className="text-right text-[10px] text-muted-foreground">
                    {actualBehavior.length}/150
                  </p>
                </div>
              </div>
            )}

            {feedbackType !== "BUG REPORT" && (
              <div className="mt-4 rounded-lg border bg-muted/20 px-3 py-3">
                <p className="text-xs font-medium">Feedback details</p>

                <p className="mt-1 text-xs leading-5 text-muted-foreground">
                  Describe the improvement, issue, or suggestion in the description above.
                </p>
              </div>
            )}

            <div className="mt-4 rounded-lg border bg-muted/20 px-3 py-2.5">
              <div className="flex items-center gap-2">
                <SelectedIcon className="size-3.5 text-primary" />

                <span className="text-[11px] font-medium">{selectedType.label}</span>

                <span className="text-[10px] text-muted-foreground">·</span>

                <span className="text-[10px] text-muted-foreground">
                  Your account will be attached automatically
                </span>
              </div>
            </div>
          </div>

          <div className="flex shrink-0 items-center justify-between gap-4 border-t bg-background px-5 py-4 sm:px-6">
            <p className="hidden text-[10px] leading-4 text-muted-foreground sm:block">
              Please avoid including passwords, tokens, API keys, or other secrets.
            </p>

            <Button
              type="submit"
              disabled={submitting || !title.trim() || !description.trim()}
              className="ml-auto"
            >
              <Send className="size-4" />

              <span>{submitting ? "Submitting..." : "Submit Feedback"}</span>
            </Button>
          </div>
        </form>
      </div>
    </section>
  );
}
