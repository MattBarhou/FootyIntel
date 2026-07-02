import { FORM_RESULT_STYLES } from "@/lib/constants";

export default function FormResultPills({ results, team }) {
  if (!results?.length) {
    return null;
  }

  return (
    <div className="flex flex-wrap gap-2" aria-label={`Recent results for ${team}`}>
      {results.map((result, index) => {
        const style = FORM_RESULT_STYLES[result] || FORM_RESULT_STYLES.D;
        return (
          <span
            key={`${team}-${index}`}
            className={`result-pill ${style.className}`}
            title={style.label}
          >
            {result}
          </span>
        );
      })}
    </div>
  );
}
