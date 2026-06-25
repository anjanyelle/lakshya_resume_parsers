import { ApplicationProvider } from "../features/apply/context/ApplicationContext";
import { Header } from "../features/apply/components/Header";
import { Wizard } from "../features/apply/components/Wizard";

export default function ApplyPage() {
  return (
    <ApplicationProvider>
      <Header />
      <Wizard />
    </ApplicationProvider>
  );
}
